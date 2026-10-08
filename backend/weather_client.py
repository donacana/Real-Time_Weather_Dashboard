"""Open-Meteo에서 현재 날씨를 수집하고 UTC 기준 JSON으로 출력한다."""

import json
import math
import sys
from datetime import datetime, timezone

import requests


API_URL = "https://api.open-meteo.com/v1/forecast"
CURRENT_FIELDS = (
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
)


def fetch_weather(latitude, longitude):
    """날씨 원본 JSON을 반환한다. 요청 실패 시 RuntimeError를 발생시킨다."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(CURRENT_FIELDS),
        "timezone": "UTC",
        "timeformat": "iso8601",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm",
        "wind_speed_unit": "ms",
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("날씨 API 요청 시간이 초과되었습니다. 잠시 후 다시 시도하세요.") from exc
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "알 수 없음"
        raise RuntimeError(f"날씨 API에서 HTTP 오류가 발생했습니다 (상태 코드: {status}).") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError("날씨 API에 연결할 수 없습니다. 네트워크 연결을 확인하세요.") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("날씨 API 응답이 올바른 JSON 형식이 아닙니다.") from exc


def parse_weather(data):
    """current를 검증하고 저장 가능한 dict로 반환한다.

    observed_at은 UTC ISO 8601, 온도는 °C, 습도는 %, 강수량은 mm,
    풍속은 m/s이다. 시간대가 없는 API 시각은 요청한 UTC로 해석한다.
    잘못된 응답은 ValueError를 발생시킨다.
    """
    if not isinstance(data, dict) or not isinstance(data.get("current"), dict):
        raise ValueError("날씨 응답에 올바른 current 객체가 없습니다.")
    current = data["current"]
    missing = [key for key in ("time", *CURRENT_FIELDS) if key not in current]
    if missing:
        raise ValueError(f"날씨 응답에 필수 항목이 누락되었습니다: {', '.join(missing)}")

    raw_time = current["time"]
    if not isinstance(raw_time, str) or "T" not in raw_time:
        raise ValueError("관측 시각이 올바른 ISO 8601 날짜·시간 문자열이 아닙니다.")
    try:
        observed_at = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)
        observed_at = observed_at.astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise ValueError("관측 시각을 UTC ISO 8601 형식으로 변환할 수 없습니다.") from exc

    for field in CURRENT_FIELDS:
        value = current[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"날씨 항목 '{field}'은 숫자여야 합니다.")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"날씨 항목 '{field}'은 유한한 숫자여야 합니다.")

    return {
        "observed_at": observed_at.isoformat().replace("+00:00", "Z"),
        "temperature": current["temperature_2m"],
        "apparent_temperature": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "precipitation": current["precipitation"],
        "wind_speed": current["wind_speed_10m"],
    }


def main():
    """서울의 현재 날씨를 출력하고 성공은 0, 실패는 1을 반환한다."""
    try:
        weather = parse_weather(fetch_weather(37.5665, 126.9780))
    except (RuntimeError, ValueError) as exc:
        print(f"날씨 조회 실패: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(weather, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
