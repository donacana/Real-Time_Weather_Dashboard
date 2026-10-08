import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    .env의 DB 정보를 사용하여 PostgreSQL 연결을 생성한다.
    """

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def test_connection():
    """
    DB 연결이 정상적으로 이루어지는지 확인한다.
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()

                print("DB 연결 성공")
                print(version[0])

    except Exception as exc:
        print(f"DB 연결 실패: {exc}")


if __name__ == "__main__":
    test_connection()