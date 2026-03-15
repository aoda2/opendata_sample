"""GTFS CSV parsers for each standard file."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


def _open_gtfs(path: Path) -> io.TextIOWrapper:
    """Open a GTFS file, stripping optional UTF-8 BOM."""
    return open(path, encoding="utf-8-sig", newline="")


@dataclass
class RawRoute:
    route_id: str
    short_name: str
    long_name: str
    route_type: int


@dataclass
class RawStop:
    stop_id: str
    name: str
    lat: float
    lng: float


@dataclass
class RawTrip:
    trip_id: str
    route_id: str
    shape_id: str
    headsign: str


@dataclass
class RawStopTime:
    trip_id: str
    stop_id: str
    arrival_time: str
    departure_time: str
    stop_sequence: int


@dataclass
class RawShape:
    shape_id: str
    lat: float
    lng: float
    sequence: int


def parse_routes(data_dir: Path) -> list[RawRoute]:
    rows = []
    with _open_gtfs(data_dir / "routes.txt") as f:
        for row in csv.DictReader(f):
            rows.append(RawRoute(
                route_id=row["route_id"].strip(),
                short_name=row.get("route_short_name", "").strip(),
                long_name=row.get("route_long_name", "").strip(),
                route_type=int(row.get("route_type", 3)),
            ))
    return rows


def parse_stops(data_dir: Path) -> list[RawStop]:
    rows = []
    with _open_gtfs(data_dir / "stops.txt") as f:
        for row in csv.DictReader(f):
            rows.append(RawStop(
                stop_id=row["stop_id"].strip(),
                name=row.get("stop_name", "").strip(),
                lat=float(row["stop_lat"]),
                lng=float(row["stop_lon"]),
            ))
    return rows


def parse_trips(data_dir: Path) -> list[RawTrip]:
    rows = []
    with _open_gtfs(data_dir / "trips.txt") as f:
        for row in csv.DictReader(f):
            rows.append(RawTrip(
                trip_id=row["trip_id"].strip(),
                route_id=row["route_id"].strip(),
                shape_id=row.get("shape_id", "").strip(),
                headsign=row.get("trip_headsign", "").strip(),
            ))
    return rows


def iter_stop_times(data_dir: Path) -> Iterator[RawStopTime]:
    """Yield stop_times rows one by one (file can be very large)."""
    with _open_gtfs(data_dir / "stop_times.txt") as f:
        for row in csv.DictReader(f):
            yield RawStopTime(
                trip_id=row["trip_id"].strip(),
                stop_id=row["stop_id"].strip(),
                arrival_time=row.get("arrival_time", "").strip(),
                departure_time=row.get("departure_time", "").strip(),
                stop_sequence=int(row["stop_sequence"]),
            )


def iter_shapes(data_dir: Path) -> Iterator[RawShape]:
    """Yield shapes rows one by one (file can be very large)."""
    shapes_path = data_dir / "shapes.txt"
    if not shapes_path.exists():
        return
    with _open_gtfs(shapes_path) as f:
        for row in csv.DictReader(f):
            yield RawShape(
                shape_id=row["shape_id"].strip(),
                lat=float(row["shape_pt_lat"]),
                lng=float(row["shape_pt_lon"]),
                sequence=int(row["shape_pt_sequence"]),
            )
