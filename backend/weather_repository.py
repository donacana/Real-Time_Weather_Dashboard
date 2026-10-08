"""기존 PostgreSQL 테이블에서 지역을 조회하고 현재 날씨를 저장한다."""

from datetime import datetime, timezone

import psycopg


def get_location_id(conn, name):
    """지역명을 조회한다. 없는 지역이나 모호한 이름은 오류로 보고한다."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT location_id FROM public.locations WHERE name = %s LIMIT 2",
                (name,),
            )
            rows = cursor.fetchall()
        if not rows:
            raise ValueError(f"등록된 지역을 찾을 수 없습니다: {name}")
        if len(rows) != 1:
            raise ValueError(f"동일한 이름의 지역이 여러 개 등록되어 있습니다: {name}")
        return rows[0][0]
    except psycopg.Error:
        conn.rollback()
        raise RuntimeError("지역 조회에 실패했습니다. DB 테이블과 조회 권한을 확인하세요.") from None


def save_weather(conn, location_id, weather):
    """INSERT 시 True, 중복이면 False를 반환한다. 커밋은 호출자가 담당한다.

    UNIQUE(location_id, observed_at)가 필요하다. 관측 시각은 UTC로,
    풍속·돌풍은 수집기의 m/s 값을 그대로 저장한다. collected_at은 DB 기본값을 쓴다.
    """
    try:
        observed_at = datetime.fromisoformat(weather["observed_at"].replace("Z", "+00:00"))
        if observed_at.tzinfo is None:
            raise ValueError("관측 시각에 시간대 정보가 필요합니다.")
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.weather_records (
                    location_id, observed_at, temperature_c,
                    apparent_temperature_c, humidity_pct,
                    precipitation_mm, wind_speed_ms, rain_mm, cloud_cover_pct,
                    surface_pressure_hpa, wind_direction_deg, wind_gusts_ms,
                    weather_code
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (location_id, observed_at) DO NOTHING
                RETURNING weather_id
                """,
                (
                    location_id,
                    observed_at.astimezone(timezone.utc),
                    weather["temperature"],
                    weather["apparent_temperature"],
                    weather["humidity"],
                    weather["precipitation"],
                    weather["wind_speed"],
                    weather["rain"],
                    weather["cloud_cover"],
                    weather["surface_pressure"],
                    weather["wind_direction"],
                    weather["wind_gusts"],
                    weather["weather_code"],
                ),
            )
            return cursor.fetchone() is not None
    except psycopg.errors.InvalidColumnReference:
        conn.rollback()
        raise RuntimeError(
            "날씨 저장에 필요한 UNIQUE(location_id, observed_at) 제약조건을 확인하세요."
        ) from None
    except psycopg.Error:
        conn.rollback()
        raise RuntimeError("날씨 저장에 실패했습니다. DB 스키마, 데이터 및 저장 권한을 확인하세요.") from None
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        conn.rollback()
        raise ValueError("저장할 날씨 데이터의 필수 항목과 관측 시각을 확인하세요.") from None
