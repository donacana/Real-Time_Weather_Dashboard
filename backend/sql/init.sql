CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    elevation_m DOUBLE PRECISION
);

CREATE TABLE weather_records (
    weather_id BIGSERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL,

    temperature_c DOUBLE PRECISION,
    apparent_temperature_c DOUBLE PRECISION,
    humidity_pct INTEGER,

    precipitation_mm DOUBLE PRECISION,
    rain_mm DOUBLE PRECISION,

    weather_code INTEGER,
    cloud_cover_pct INTEGER,

    surface_pressure_hpa DOUBLE PRECISION,

    wind_speed_ms DOUBLE PRECISION,
    wind_direction_deg INTEGER,
    wind_gusts_ms DOUBLE PRECISION,

    interval_seconds INTEGER,
    collected_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_weather_location
        FOREIGN KEY (location_id)
        REFERENCES locations(location_id)
        ON DELETE CASCADE
);