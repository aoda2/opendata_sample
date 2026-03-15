"""gRPC TransitService implementation."""
from __future__ import annotations

import hashlib
import random
import sqlite3
from datetime import datetime, timezone
from typing import Any

import grpc

from gen.transit.v1 import transit_pb2, transit_pb2_grpc
from internal.db import queries


def _seeded_delay(seed_str: str, hour: int) -> tuple[float, float]:
    """Return (avg_delay_sec, delay_rate) using a stable hash seed.

    Rush hours (7-9, 17-19) produce higher delays to make the simulation
    visually interesting.
    """
    digest = hashlib.md5(f"{seed_str}-{hour}".encode()).digest()
    rng = random.Random(int.from_bytes(digest[:8], "little"))
    rush = (7 <= hour <= 9) or (17 <= hour <= 19)
    base = 120.0 if rush else 30.0
    avg_delay = base + rng.random() * 60.0
    delay_rate = 0.3 + rng.random() * 0.5 if rush else 0.05 + rng.random() * 0.3
    return avg_delay, delay_rate


class TransitServicer(transit_pb2_grpc.TransitServiceServicer):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    def ListRoutes(
        self, request: Any, context: grpc.ServicerContext
    ) -> transit_pb2.ListRoutesResponse:
        with self._conn() as conn:
            rows = queries.list_routes(conn)

        routes = []
        for r in rows:
            avg_delay, _ = _seeded_delay(r.route_id, 12)
            routes.append(
                transit_pb2.Route(
                    route_id=r.route_id,
                    route_short_name=r.short_name,
                    route_long_name=r.long_name,
                    avg_delay_sec=avg_delay,
                )
            )
        return transit_pb2.ListRoutesResponse(routes=routes)

    # ------------------------------------------------------------------
    def GetRouteShape(
        self, request: transit_pb2.GetRouteShapeRequest, context: grpc.ServicerContext
    ) -> transit_pb2.RouteShape:
        with self._conn() as conn:
            route = queries.get_route(conn, request.route_id)
            if route is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Route {request.route_id!r} not found")
                return transit_pb2.RouteShape()

            shape_id = queries.get_shape_id_for_route(conn, request.route_id)
            points: list[transit_pb2.LatLng] = []
            if shape_id:
                for pt in queries.get_shape_points(conn, shape_id):
                    points.append(transit_pb2.LatLng(lat=pt.lat, lng=pt.lng))

        return transit_pb2.RouteShape(
            route_id=route.route_id,
            route_name=f"{route.short_name} {route.long_name}".strip(),
            points=points,
        )

    # ------------------------------------------------------------------
    def GetStopsByRoute(
        self, request: transit_pb2.GetStopsByRouteRequest, context: grpc.ServicerContext
    ) -> transit_pb2.GetStopsByRouteResponse:
        with self._conn() as conn:
            stop_rows = queries.get_stops_by_route(conn, request.route_id)

        stops = [
            transit_pb2.Stop(
                stop_id=s.stop_id,
                stop_name=s.stop_name,
                lat=s.lat,
                lng=s.lng,
                sequence=s.sequence,
            )
            for s in stop_rows
        ]
        return transit_pb2.GetStopsByRouteResponse(stops=stops)

    # ------------------------------------------------------------------
    def GetStopStats(
        self, request: transit_pb2.GetStopStatsRequest, context: grpc.ServicerContext
    ) -> transit_pb2.StopStats:
        hour = datetime.now(timezone.utc).hour
        try:
            from_dt = datetime.fromisoformat(
                request.time_range.from_.replace("Z", "+00:00")
            )
            hour = from_dt.hour
        except Exception:
            pass

        avg_delay, delay_rate = _seeded_delay(request.stop_id, hour)

        with self._conn() as conn:
            stop = queries.get_stop(conn, request.stop_id)
            if stop is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Stop {request.stop_id!r} not found")
                return transit_pb2.StopStats()

            trip_count = queries.get_trip_count_for_stop(conn, request.stop_id)

            now_time = datetime.now(timezone.utc).strftime("%H:%M:%S")
            next_dep = queries.get_next_departure(conn, request.stop_id, now_time)

        return transit_pb2.StopStats(
            stop_id=stop.stop_id,
            stop_name=stop.stop_name,
            avg_delay_sec=avg_delay,
            delay_rate=delay_rate,
            trip_count=trip_count,
            next_departure=next_dep or "",
        )

    # ------------------------------------------------------------------
    def GetDelayHeatmap(
        self, request: transit_pb2.GetDelayHeatmapRequest, context: grpc.ServicerContext
    ) -> transit_pb2.GetDelayHeatmapResponse:
        bbox = request.bbox
        hour = datetime.now(timezone.utc).hour
        try:
            from_dt = datetime.fromisoformat(
                request.time_range.from_.replace("Z", "+00:00")
            )
            hour = from_dt.hour
        except Exception:
            pass

        with self._conn() as conn:
            stops = queries.get_stops_in_bbox(
                conn,
                bbox.min_lat, bbox.min_lng,
                bbox.max_lat, bbox.max_lng,
            )

        # Aggregate stops into 0.01-degree grid cells
        grid: dict[tuple[int, int], list[float]] = {}
        for s in stops:
            key = (round(s.lat / 0.01), round(s.lng / 0.01))
            avg_delay, _ = _seeded_delay(s.stop_id, hour)
            grid.setdefault(key, []).append(avg_delay)

        # Normalise delay scores to [0, 1]
        all_delays = [v for vals in grid.values() for v in vals]
        max_delay = max(all_delays) if all_delays else 1.0

        cells = []
        for (lat_key, lng_key), delays in grid.items():
            avg = sum(delays) / len(delays)
            cells.append(
                transit_pb2.HeatmapCell(
                    lat=lat_key * 0.01,
                    lng=lng_key * 0.01,
                    delay_score=avg / max_delay,
                    sample_count=len(delays),
                )
            )

        return transit_pb2.GetDelayHeatmapResponse(cells=cells)
