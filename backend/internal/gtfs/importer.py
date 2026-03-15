"""Orchestrates GTFS CSV parsing and SQLite insertion."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from internal.gtfs.parser import (
    parse_routes,
    parse_stops,
    parse_trips,
    iter_stop_times,
    iter_shapes,
)

SCHEMA_SQL = Path(__file__).parent.parent / "db" / "schema.sql"
BATCH_SIZE = 500


def _exec_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL.read_text())


def import_gtfs(conn: sqlite3.Connection, data_dir: Path) -> dict[str, int]:
    """Import all GTFS files into the database. Returns counts per entity."""
    _exec_schema(conn)
    counts: dict[str, int] = {}

    # --- routes ---
    routes = parse_routes(data_dir)
    conn.executemany(
        "INSERT OR REPLACE INTO routes VALUES (?, ?, ?, ?)",
        [(r.route_id, r.short_name, r.long_name, r.route_type) for r in routes],
    )
    conn.commit()
    counts["routes"] = len(routes)

    # --- stops ---
    stops = parse_stops(data_dir)
    conn.executemany(
        "INSERT OR REPLACE INTO stops VALUES (?, ?, ?, ?)",
        [(s.stop_id, s.name, s.lat, s.lng) for s in stops],
    )
    conn.commit()
    counts["stops"] = len(stops)

    # --- trips ---
    trips = parse_trips(data_dir)
    conn.executemany(
        "INSERT OR REPLACE INTO trips VALUES (?, ?, ?, ?)",
        [(t.trip_id, t.route_id, t.shape_id, t.headsign) for t in trips],
    )
    conn.commit()
    counts["trips"] = len(trips)

    # --- shapes (batched) ---
    shape_count = 0
    batch: list[tuple] = []
    for shape in iter_shapes(data_dir):
        batch.append((shape.shape_id, shape.lat, shape.lng, shape.sequence))
        if len(batch) >= BATCH_SIZE:
            conn.executemany(
                "INSERT OR REPLACE INTO shapes VALUES (?, ?, ?, ?)", batch
            )
            conn.commit()
            shape_count += len(batch)
            batch.clear()
    if batch:
        conn.executemany(
            "INSERT OR REPLACE INTO shapes VALUES (?, ?, ?, ?)", batch
        )
        conn.commit()
        shape_count += len(batch)
    counts["shape_points"] = shape_count

    # --- stop_times (batched, largest file) ---
    st_count = 0
    batch = []
    for st in iter_stop_times(data_dir):
        batch.append((st.trip_id, st.stop_id, st.arrival_time, st.departure_time, st.stop_sequence))
        if len(batch) >= BATCH_SIZE:
            conn.executemany(
                "INSERT OR REPLACE INTO stop_times VALUES (?, ?, ?, ?, ?)", batch
            )
            conn.commit()
            st_count += len(batch)
            if st_count % 50_000 == 0:
                print(f"  stop_times: {st_count:,} rows inserted...")
            batch.clear()
    if batch:
        conn.executemany(
            "INSERT OR REPLACE INTO stop_times VALUES (?, ?, ?, ?, ?)", batch
        )
        conn.commit()
        st_count += len(batch)
    counts["stop_times"] = st_count

    return counts
