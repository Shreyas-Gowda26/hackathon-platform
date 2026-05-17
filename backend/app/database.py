import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
import os

load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="hackathon_pool",
    pool_size=5,
    **db_config
)

def get_db():
    connection = connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()