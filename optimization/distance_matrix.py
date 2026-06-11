import numpy as np

def create_distance_matrix(customers):

    locations = customers[['latitude', 'longitude']].values

    distance_matrix = []

    for i in range(len(locations)):
        row = []

        for j in range(len(locations)):
            lat1, lon1 = locations[i]
            lat2, lon2 = locations[j]

            distance = np.sqrt(
                (lat1 - lat2) ** 2 +
                (lon1 - lon2) ** 2
            )

            row.append(int(distance * 111))

        distance_matrix.append(row)

    return distance_matrix