import numpy as np

# map_processing.py


# Convert RGB to grayscale manually
def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

# Calculate edges coordinates points
def calculate_edges_coordinates(labeled_edges, number):
    coordinate_points = []
    if number > 2:
        for n in range(3, number + 1, 1):
            coord = np.where(labeled_edges == n)
            for c1, c2 in zip(coord[0], coord[1]):
                points = []
                points.extend([c2, c1])
                coordinate_points.append(points)
    else:
        coord = np.where(labeled_edges == number)
        for c1, c2 in zip(coord[0], coord[1]):
                points = []
                points.extend([c2, c1])
                coordinate_points.append(points)
    return coordinate_points

# Calculating minimum and maximum points by coordinates points 
def min_max_coord(coordinate_points):
    x_coord = []
    y_coord = []
    for cp in coordinate_points:
        x_coord.append(cp[0])
        y_coord.append(cp[1])
    min_x_coord = min(x_coord)
    max_x_coord = max(x_coord)
    min_y_coord = min(y_coord)
    max_y_coord = max(y_coord)
    min_max_x_y = [min_x_coord, min_y_coord, max_x_coord, max_y_coord]
    return min_max_x_y