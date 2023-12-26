import psycopg2
from os import getenv
from dotenv import load_dotenv

load_dotenv()

host = getenv("LOCALHOST")
user = getenv("MYBOTUSER")
password = getenv("MYPASSWORD")
database = getenv("MYNAMEDB")


def connect():
    return psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )


def close(conn):
    if conn:
        conn.close()