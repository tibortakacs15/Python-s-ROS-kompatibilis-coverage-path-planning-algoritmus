import numpy as np
from calculate_intersection_points import calculate_distance

# arrea.py

def calculating_route_distance(visited_points):
    rout_distance = 0
    for vp in range(len(visited_points) - 1):
        rout_distance += calculate_distance(visited_points[vp], visited_points[vp + 1])
    return rout_distance

    