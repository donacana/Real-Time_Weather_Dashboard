"""날씨 API 수집부터 PostgreSQL 저장까지 한 번 실행한다."""

import sys

import psycopg

if __package__:
    from .db import get_connection
    from .weather_client import fetch_weather, parse_weather
    from .weather_repository import get_location_id, save_weather
else:
    from db import get_connection
    from weather_client import fetch_weather, parse_weather
    from weather_repository import get_location_id, save_weather


def collect_weather(latitude, longitude, location_name):
    """수집·정제·저장 후 커밋한다. 저장은 True, 중복은 False를 반환한다.

    연결 컨텍스트가 성공 시 커밋, 예외 시 롤백하고 항상 연결을 종료한다.
    """
    weather = parse_weather(fetch_weather(latitude, longitude))
    try:
        with get_connection() as conn:
            location_id = get_location_id(conn, location_name)
            saved = save_weather(conn, location_id, weather)
        return saved
    except psycopg.Error:
        raise RuntimeError("날씨 적재 트랜잭션에 실패했습니다. DB 연결 상태를 확인하세요.") from None


def main():
    """기존 Seoul 지역으로 적재하고 성공·중복·실패 결과를 출력한다."""
    try:
        saved = collect_weather(37.5665, 126.9780, "Seoul")
    except (RuntimeError, ValueError) as exc:
        print(f"날씨 적재 실패: {exc}", file=sys.stderr)
        return 1
    if saved:
        print("날씨 저장 성공: Seoul의 현재 날씨를 저장했습니다.")
    else:
        print("중복 데이터: Seoul의 동일 관측 시각 데이터가 이미 저장되어 있습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
