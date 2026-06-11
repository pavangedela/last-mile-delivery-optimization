from database.db_connection import get_connection


def save_route(
    vehicle_id,
    customer_sequence,
    total_distance,
    total_load,
    route_coordinates
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO routes
        (
            vehicle_id,
            customer_sequence,
            total_distance,
            total_load,
            route_coordinates
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            vehicle_id,
            customer_sequence,
            total_distance,
            total_load,
            route_coordinates
        )
    )

    conn.commit()

    cursor.close()
    conn.close()