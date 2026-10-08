from backend.app.repositories.weather_repository import get_latest_weather


def get_current_weather():
    row = get_latest_weather()

    if row is None:
        return None

    return {
        "latitude": row[0],
        "longitude": row[1],

        "utc_offset_seconds": 32400,

        "timezone": row[2],
        "timezone_abbreviation": "GMT+9",

        "elevation": row[3],

        "current_units": {
            "time": "iso8601",
            "interval": "seconds",

            "temperature_2m": "°C",
            "apparent_temperature": "°C",

            "relative_humidity_2m": "%",

            "precipitation": "mm",
            "rain": "mm",

            "weather_code": "wmo code",

            "cloud_cover": "%",

            "surface_pressure": "hPa",

            "wind_speed_10m": "m/s",
            "wind_direction_10m": "°",
            "wind_gusts_10m": "m/s",
        },

        "current": {
            "time": row[4].isoformat(),
            "interval": row[5],

            "temperature_2m": row[6],
            "apparent_temperature": row[7],

            "relative_humidity_2m": row[8],

            "precipitation": row[9],
            "rain": row[10],

            "weather_code": row[11],

            "cloud_cover": row[12],

            "surface_pressure": row[13],

            "wind_speed_10m": row[14],
            "wind_direction_10m": row[15],
            "wind_gusts_10m": row[16],
        },
    }