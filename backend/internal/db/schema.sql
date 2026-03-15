PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS routes (
    route_id         TEXT PRIMARY KEY,
    route_short_name TEXT NOT NULL,
    route_long_name  TEXT NOT NULL,
    route_type       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS stops (
    stop_id   TEXT PRIMARY KEY,
    stop_name TEXT NOT NULL,
    stop_lat  REAL NOT NULL,
    stop_lng  REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id       TEXT PRIMARY KEY,
    route_id      TEXT NOT NULL REFERENCES routes(route_id),
    shape_id      TEXT,
    trip_headsign TEXT
);

CREATE TABLE IF NOT EXISTS stop_times (
    trip_id        TEXT NOT NULL REFERENCES trips(trip_id),
    stop_id        TEXT NOT NULL REFERENCES stops(stop_id),
    arrival_time   TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    stop_sequence  INTEGER NOT NULL,
    PRIMARY KEY (trip_id, stop_sequence)
);

CREATE TABLE IF NOT EXISTS shapes (
    shape_id          TEXT NOT NULL,
    shape_pt_lat      REAL NOT NULL,
    shape_pt_lon      REAL NOT NULL,
    shape_pt_sequence INTEGER NOT NULL,
    PRIMARY KEY (shape_id, shape_pt_sequence)
);

CREATE INDEX IF NOT EXISTS idx_trips_route    ON trips(route_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_trip ON stop_times(trip_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_stop ON stop_times(stop_id);
CREATE INDEX IF NOT EXISTS idx_shapes_id      ON shapes(shape_id);
