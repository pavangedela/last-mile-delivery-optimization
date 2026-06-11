import pandas as pd
from database.db_connection import get_connection

df = pd.read_csv("data/customers_500.csv")

conn = get_connection()
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO customers
        (customer_id, latitude, longitude, demand, start_hour, end_hour)
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (customer_id) DO NOTHING;
    """, (
        row['customer_id'],
        row['latitude'],
        row['longitude'],
        row['demand'],
        row['start_hour'],
        row['end_hour']
    ))

conn.commit()

print("Customer data loaded successfully!")

cursor.close()
conn.close()