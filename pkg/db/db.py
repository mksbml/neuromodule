import psycopg2
from psycopg2.extras import RealDictCursor
from pkg.config.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def ConnectDB():
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )
    return connection

