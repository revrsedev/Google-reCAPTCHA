import psycopg2
from decouple import config

POSTGRESQL_CONFIG = {
    'dbname': config('DB_NAME'),
    'user': config('DB_USER'),
    'password': config('DB_PASSWORD'),
    'host': config('DB_HOST'),
    'port': config('DB_PORT', default=5432),
}

def get_connection():
    return psycopg2.connect(**POSTGRESQL_CONFIG)
