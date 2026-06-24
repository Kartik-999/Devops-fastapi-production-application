import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL","postgresql://postgres:POSTGRES_PASSWORD@back_end:5432/studentdb")

def get_connection():
    return psycopg2.connect(DATABASE_URL)