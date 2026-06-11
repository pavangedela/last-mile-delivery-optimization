import pandas as pd
import numpy as np

np.random.seed(42)

customers = []

for i in range(1, 501):
    customers.append({
        "customer_id": f"C{i}",
        "latitude": round(np.random.uniform(17.2, 17.6), 6),
        "longitude": round(np.random.uniform(78.2, 78.7), 6),
        "demand": np.random.randint(5, 30),
        "start_hour": np.random.randint(8, 14),
        "end_hour": np.random.randint(14, 20)
    })

df = pd.DataFrame(customers)

df.to_csv("data/customers_500.csv", index=False)

print("500 customers generated")