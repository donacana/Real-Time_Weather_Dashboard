import requests
import json

url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.5665"
    "&longitude=126.9780"
    "&current="
    "temperature_2m,"
    "apparent_temperature,"
    "relative_humidity_2m,"
    "precipitation,"
    "rain,"
    "weather_code,"
    "cloud_cover,"
    "surface_pressure,"
    "wind_speed_10m,"
    "wind_direction_10m,"
    "wind_gusts_10m"
    "&timezone=Asia%2FSeoul"
)

data = requests.get(url).json()

print(json.dumps(data, indent=2, ensure_ascii=False))