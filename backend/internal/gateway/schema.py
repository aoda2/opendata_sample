"""Strawberry GraphQL schema — types, queries, and resolvers.

Resolvers call the gRPC TransitService via a grpc.Channel injected at
startup. All types mirror the proto definitions.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import grpc
import strawberry

from gen.transit.v1 import transit_pb2, transit_pb2_grpc


# ---------------------------------------------------------------------------
# GraphQL types
# ---------------------------------------------------------------------------


@strawberry.type
class LatLng:
    lat: float
    lng: float


@strawberry.type
class RouteShape:
    points: list[LatLng]


@strawberry.type
class Stop:
    id: strawberry.ID
    name: str
    lat: float
    lng: float
    sequence: int


@strawberry.type
class Route:
    id: strawberry.ID
    short_name: str
    long_name: str
    avg_delay_sec: float


@strawberry.type
class StopStats:
    stop_id: strawberry.ID
    stop_name: str
    avg_delay_sec: float
    delay_rate: float
    trip_count: int
    next_departure: Optional[str]


@strawberry.type
class HeatmapCell:
    lat: float
    lng: float
    delay_score: float
    sample_count: int


@strawberry.input
class BBoxInput:
    min_lat: float
    min_lng: float
    max_lat: float
    max_lng: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stub(channel: grpc.Channel) -> transit_pb2_grpc.TransitServiceStub:
    return transit_pb2_grpc.TransitServiceStub(channel)


def _proto_to_route(r: transit_pb2.Route) -> Route:
    return Route(
        id=r.route_id,
        short_name=r.route_short_name,
        long_name=r.route_long_name,
        avg_delay_sec=r.avg_delay_sec,
    )


def _proto_to_stop(s: transit_pb2.Stop) -> Stop:
    return Stop(id=s.stop_id, name=s.stop_name, lat=s.lat, lng=s.lng, sequence=s.sequence)


# ---------------------------------------------------------------------------
# Query resolvers
# ---------------------------------------------------------------------------


@strawberry.type
class Query:
    @strawberry.field
    def routes(self, info: strawberry.types.Info) -> list[Route]:
        stub = _stub(info.context["grpc_channel"])
        resp = stub.ListRoutes(transit_pb2.ListRoutesRequest())
        return [_proto_to_route(r) for r in resp.routes]

    @strawberry.field
    def route(self, info: strawberry.types.Info, id: strawberry.ID) -> Optional[Route]:
        stub = _stub(info.context["grpc_channel"])
        resp = stub.ListRoutes(transit_pb2.ListRoutesRequest())
        for r in resp.routes:
            if r.route_id == id:
                return _proto_to_route(r)
        return None

    @strawberry.field
    def route_shape(self, info: strawberry.types.Info, route_id: strawberry.ID) -> Optional[RouteShape]:
        stub = _stub(info.context["grpc_channel"])
        shape = stub.GetRouteShape(transit_pb2.GetRouteShapeRequest(route_id=route_id))
        points = [LatLng(lat=p.lat, lng=p.lng) for p in shape.points]
        return RouteShape(points=points)

    @strawberry.field
    def stops_by_route(self, info: strawberry.types.Info, route_id: strawberry.ID) -> list[Stop]:
        stub = _stub(info.context["grpc_channel"])
        resp = stub.GetStopsByRoute(transit_pb2.GetStopsByRouteRequest(route_id=route_id))
        return [_proto_to_stop(s) for s in resp.stops]

    @strawberry.field
    def stop_stats(
        self,
        info: strawberry.types.Info,
        stop_id: strawberry.ID,
        from_: str,
        to: str,
    ) -> Optional[StopStats]:
        stub = _stub(info.context["grpc_channel"])
        time_range = transit_pb2.TimeRange(**{"from": from_, "to": to})
        stats = stub.GetStopStats(
            transit_pb2.GetStopStatsRequest(stop_id=stop_id, time_range=time_range)
        )
        return StopStats(
            stop_id=stats.stop_id,
            stop_name=stats.stop_name,
            avg_delay_sec=stats.avg_delay_sec,
            delay_rate=stats.delay_rate,
            trip_count=stats.trip_count,
            next_departure=stats.next_departure or None,
        )

    @strawberry.field
    def delay_heatmap(
        self,
        info: strawberry.types.Info,
        from_: str,
        to: str,
        bbox: BBoxInput,
    ) -> list[HeatmapCell]:
        stub = _stub(info.context["grpc_channel"])
        time_range = transit_pb2.TimeRange(**{"from": from_, "to": to})
        proto_bbox = transit_pb2.BBox(
            min_lat=bbox.min_lat, min_lng=bbox.min_lng,
            max_lat=bbox.max_lat, max_lng=bbox.max_lng,
        )
        resp = stub.GetDelayHeatmap(
            transit_pb2.GetDelayHeatmapRequest(time_range=time_range, bbox=proto_bbox)
        )
        return [
            HeatmapCell(
                lat=c.lat, lng=c.lng,
                delay_score=c.delay_score, sample_count=c.sample_count,
            )
            for c in resp.cells
        ]


# ---------------------------------------------------------------------------
# Build the schema (exported for use in FastAPI app)
# ---------------------------------------------------------------------------

schema = strawberry.Schema(query=Query)
