import psycopg2

def get_connection():
    return psycopg2.connect(
        host="ep-polished-bird-aosckuge.c-2.ap-southeast-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_cDagZwzpMA75",
        sslmode="require"
    )