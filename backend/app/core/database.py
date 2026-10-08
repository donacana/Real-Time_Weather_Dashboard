import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(ENV_PATH)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )