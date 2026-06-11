import pandas as pd

from database.db_connection import get_connection
from optimization.distance_matrix import create_distance_matrix
from optimization.route_optimizer import solve_route


def main():

    # Database Connection
    conn = get_connection()

    # Read Customers
    customers = pd.read_sql("""
    SELECT *
    FROM customers
    ORDER BY customer_id
    LIMIT 50
    """, conn)

    # Read Vehicles
    vehicles = pd.read_sql("""
    SELECT *
    FROM vehicles
    """, conn)

    conn.close()

    print("\n========== CUSTOMERS ==========")
    print(customers.head())

    print("\n========== VEHICLES ==========")
    print(vehicles)

    print("\nTotal Customers:", len(customers))
    print("Total Vehicles:", len(vehicles))

    # Distance Matrix
    distance_matrix = create_distance_matrix(customers)

    print("\nDistance Matrix Size:")
    print(
        len(distance_matrix),
        "x",
        len(distance_matrix[0])
    )

    # Customer Demands
    demands = customers["demand"].tolist()

    # First node treated as depot
    demands[0] = 0

    # Vehicle Capacities
    vehicle_capacities = vehicles["capacity"].tolist()

    # Time Windows
    time_windows = list(
        zip(
            customers["start_hour"],
            customers["end_hour"]
        )
    )

    print("\n========== LOAD SUMMARY ==========")
    print("Total Demand:", sum(demands))
    print("Total Vehicle Capacity:", sum(vehicle_capacities))

    print("\nCustomer Demands:")
    print(demands)

    print("\nVehicle Capacities:")
    print(vehicle_capacities)

    print("\nTime Windows:")
    print(time_windows[:10])

    # Solve Route
    solution = solve_route(
        distance_matrix,
        len(vehicles),
        demands,
        vehicle_capacities,
        time_windows
    )

    if solution:
        print("\nRoute Found!")
    else:
        print("\nNo Route Found")


if __name__ == "__main__":
    main()