CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS violations (
    id                  VARCHAR(20) PRIMARY KEY,
    latitude            DOUBLE PRECISION NOT NULL,
    longitude           DOUBLE PRECISION NOT NULL,
    location            TEXT,
    vehicle_number      VARCHAR(30),
    vehicle_type        VARCHAR(30),
    violation_type      TEXT,
    offence_code        TEXT,
    created_datetime    TIMESTAMPTZ,
    closed_datetime     TIMESTAMPTZ,
    police_station      VARCHAR(60),
    junction_name       VARCHAR(120),
    data_sent_to_scita  BOOLEAN DEFAULT FALSE,
    validation_status   VARCHAR(20),
    cis_score           FLOAT,
    geom                GEOMETRY(Point, 4326)
);

CREATE INDEX IF NOT EXISTS violations_geom_idx    ON violations USING GIST(geom);
CREATE INDEX IF NOT EXISTS violations_station_idx ON violations(police_station);
CREATE INDEX IF NOT EXISTS violations_created_idx ON violations(created_datetime);

CREATE TABLE IF NOT EXISTS hotspots (
    id              SERIAL PRIMARY KEY,
    cluster_id      INTEGER,
    centroid_lat    DOUBLE PRECISION,
    centroid_lng    DOUBLE PRECISION,
    violation_count INTEGER,
    avg_cis_score   FLOAT,
    top_violation   TEXT,
    police_station  TEXT,
    computed_at     TIMESTAMPTZ DEFAULT NOW(),
    geom            GEOMETRY(Point, 4326)
);

CREATE INDEX IF NOT EXISTS hotspots_geom_idx ON hotspots USING GIST(geom);
