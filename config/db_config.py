import psycopg2
import os
from dotenv import load_dotenv 

load_dotenv()

def get_connection():
    for var in ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']:
        print(var, repr(os.getenv(var)))
    conn = psycopg2.connect(
        host = os.getenv('DB_HOST'),
        dbname = os.getenv('DB_NAME'),
        port = os.getenv('DB_PORT'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD')
    )
    return conn 

