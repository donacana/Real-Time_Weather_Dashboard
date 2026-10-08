from backend.app.core.database import get_connection


def get_latest_weather():
    query = """
        SELECT
            l.latitude,
            l.longitude,
            l.timezone,
            l.elevation_m,

            w.observed_at,
            w.interval_seconds,

            w.temperature_c,
            w.apparent_temperature_c,
            w.humidity_pct,

            w.precipitation_mm,
            w.rain_mm,

            w.weather_code,
            w.cloud_cover_pct,

            w.surface_pressure_hpa,

            w.wind_speed_ms,
            w.wind_direction_deg,
            w.wind_gusts_ms

        FROM weather_records w

        JOIN locations l
            ON w.location_id = l.location_id

        ORDER BY w.observed_at DESC

        LIMIT 1
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()