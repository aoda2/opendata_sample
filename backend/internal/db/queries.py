"""SQLite query helpers used by the gRPC service."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class RouteRow:
    route_id: str
    short_name: str
    long_name: str


@dataclass
class ShapePoint:
    lat: float
    lng: float


@dataclass
class StopRow:
    stop_id: str
    stop_name: str
    lat: float
    lng: float
    sequence: int


def list_routes(conn: sqlite3.Connection) -> list[RouteRow]:
    cur = conn.execute(
        "SELECT route_id, route_short_name, route_long_name FROM routes ORDER BY route_short_name"
    )
    return [RouteRow(*row) for row in cur.fetchall()]


def get_route(conn: sqlite3.Connection, route_id: str) -> Optional[RouteRow]:
    cur = conn.execute(
        "SELECT route_id, route_short_name, route_long_name FROM routes WHERE route_id = ?",
        (route_id,),
    )
    row = cur.fetchone()
    return RouteRow(*row) if row else None


def get_shape_id_for_route(conn: sqlite3.Connection, route_id: str) -> Optional[str]:
    """Return the shape_id of a representative trip for the route."""
    cur = conn.execute(
        "SELECT shape_id FROM trips WHERE route_id = ? AND shape_id != '' LIMIT 1",
        (route_id,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_shape_points(conn: sqlite3.Connection, shape_id: str) -> list[ShapePoint]:
    cur = conn.execute(
        "SELECT shape_pt_lat, shape_pt_lon FROM shapes "
        "WHERE shape_id = ? ORDER BY shape_pt_sequence",
        (shape_id,),
    )
    return [ShapePoint(lat=r[0], lng=r[1]) for r in cur.fetchall()]


def get_stops_by_route(conn: sqlite3.Connection, route_id: str) -> list[StopRow]:
    cur = conn.execute(
        """
        SELECT DISTINCT s.stop_id, s.stop_name, s.stop_lat, s.stop_lng,
               MIN(st.stop_sequence) AS seq
        FROM stops s
        JOIN stop_times st ON s.stop_id = st.stop_id
        JOIN trips t       ON st.trip_id = t.trip_id
        WHERE t.route_id = ?
        GROUP BY s.stop_id
        ORDER BY seq
        """,
        (route_id,),
    )
    return [StopRow(*row) for row in cur.fetchall()]


def get_stop(conn: sqlite3.Connection, stop_id: str) -> Optional[StopRow]:
    cur = conn.execute(
        "SELECT stop_id, stop_name, stop_lat, stop_lng, 0 FROM stops WHERE stop_id = ?",
        (stop_id,),
    )
    row = cur.fetchone()
    return StopRow(*row) if row else None


def get_trip_count_for_stop(conn: sqlite3.Connection, stop_id: str) -> int:
    cur = conn.execute(
        "SELECT COUNT(DISTINCT trip_id) FROM stop_times WHERE stop_id = ?",
        (stop_id,),
    )
    return cur.fetchone()[0]


def get_next_departure(conn: sqlite3.Connection, stop_id: str, after_time: str) -> Optional[str]:
    """Return the next departure_time (HH:MM:SS) at stop_id after after_time."""
    cur = conn.execute(
        """
        SELECT departure_time FROM stop_times
        WHERE stop_id = ? AND departure_time > ?
        ORDER BY departure_time LIMIT 1
        """,
        (stop_id, after_time),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_stops_in_bbox(
    conn: sqlite3.Connection,
    min_lat: float, min_lng: float,
    max_lat: float, max_lng: float,
) -> list[StopRow]:
    cur = conn.execute(
        """
        SELECT stop_id, stop_name, stop_lat, stop_lng, 0
        FROM stops
        WHERE stop_lat BETWEEN ? AND ?
          AND stop_lng BETWEEN ? AND ?
        """,
        (min_lat, max_lat, min_lng, max_lng),
    )
    return [StopRow(*row) for row in cur.fetchall()]
