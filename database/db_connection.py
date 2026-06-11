import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="logistics_db",
        user="gedelapavan"
    )
    return conn