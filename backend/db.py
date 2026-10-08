"""환경변수로 PostgreSQL 연결을 생성한다."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def get_connection():
    """backend의 .env(없으면 저장소 루트)를 읽고 UTC 연결을 반환한다.

    이미 설정된 환경변수를 우선하며, 연결의 커밋·롤백·종료는 호출자가
    담당한다. 설정 또는 연결 오류는 접속 정보를 노출하지 않고 보고한다.
    """
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        env_path = env_path.parent.parent / ".env"
    load_dotenv(env_path, override=False)
    required = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    values = {name: os.getenv(name) for name in required}
    missing = [name for name in required if not values[name]]
    if missing:
        raise RuntimeError(f"DB 환경변수가 누락되었습니다: {', '.join(missing)}")

    try:
        port = int(values["DB_PORT"])
    except ValueError:
        raise RuntimeError("DB_PORT는 1~65535 사이의 정수여야 합니다.") from None
    if not 1 <= port <= 65535:
        raise RuntimeError("DB_PORT는 1~65535 사이의 정수여야 합니다.")

    try:
        return psycopg.connect(
            host=values["DB_HOST"],
            port=port,
            dbname=values["DB_NAME"],
            user=values["DB_USER"],
            password=values["DB_PASSWORD"],
            connect_timeout=10,
            options="-c timezone=UTC",
        )
    except psycopg.Error:
        raise RuntimeError(
            "PostgreSQL 연결에 실패했습니다. DB 환경변수, 서버 상태 및 접속 권한을 확인하세요."
        ) from None
