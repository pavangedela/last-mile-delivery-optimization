from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

from database.save_routes import save_route


def solve_route(
    distance_matrix,
    num_vehicles,
    demands,
    vehicle_capacities,
    time_windows
):

    print("\nReceived Time Windows:")
    print(time_windows[:10])

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        num_vehicles,
        0
    )

    routing = pywrapcp.RoutingModel(manager)

    # Distance Callback
    def distance_callback(from_index, to_index):

        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(
        distance_callback
    )

    routing.SetArcCostEvaluatorOfAllVehicles(
        transit_callback_index
    )

    # Demand Callback
    def demand_callback(from_index):

        from_node = manager.IndexToNode(from_index)

        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback
    )

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        vehicle_capacities,
        True,
        "Capacity"
    )

    search_parameters = (
        pywrapcp.DefaultRoutingSearchParameters()
    )

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(
        search_parameters
    )

    if not solution:
        print("No Solution Found")
        return None

    print("\n========== ROUTES ==========\n")

    total_distance = 0

    for vehicle_id in range(num_vehicles):

        index = routing.Start(vehicle_id)

        route_distance = 0
        route_load = 0

        route = f"Vehicle {vehicle_id + 1}: "

        # Save node sequence
        route_nodes = []

        while not routing.IsEnd(index):

            node = manager.IndexToNode(index)

            route_nodes.append(node)

            route_load += demands[node]

            route += f"{node} -> "

            previous_index = index

            index = solution.Value(
                routing.NextVar(index)
            )

            route_distance += routing.GetArcCostForVehicle(
                previous_index,
                index,
                vehicle_id
            )

        end_node = manager.IndexToNode(index)

        route_nodes.append(end_node)

        route += f"{end_node}"

        print(route)
        print(f"Load: {route_load} kg")
        print(f"Distance: {route_distance} km\n")

        save_route(
            f"V{vehicle_id + 1}",
            route,
            route_distance,
            route_load,
            str(route_nodes)
        )

        total_distance += route_distance

    print(f"Total Distance: {total_distance} km")

    return solution