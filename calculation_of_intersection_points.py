import numpy as np
import matplotlib.pyplot as plt
import math

from calculation_of_parallel_lines import bresenham
from save_map_and_obstacle_boundaries import calculate_distance

# calculate_of_intersection_points.py


#  The shape points located between parallel lines
def edges_of_the_shapes(lines, shapes):
    edge_coordinates  = []
    for line in lines:
        edge = []
        end, start = line[-1][1], line[0][1] # paralell lines start and end points
        if start > end:
            start, end = end, start
        for shape in shapes:
            condition = (shape[:, 1] >= start) & (shape[:, 1] <= end)  
            result = shape[condition]
            if len(result) > 0:
                edge.append(result)
        edge_coordinates.append(edge)
    return edge_coordinates


def calculate_intersection_points(edge_coordinates, lines, angle_degrees):
    intersection_points = [set() for _ in range(len(lines))]
    for count, (edge_c, line) in enumerate(zip(edge_coordinates, lines)):
        if len(edge_c) == 0 or len(line) < 2:
            continue
        for l in range(len(line) - 1):
            for ec in edge_c:
                if len(ec) < 2:
                    continue
                for e in range(len(ec) - 1):
                    ip = find_intersection_of_segments(ec[e], ec[e + 1], line[l], line[l + 1])
                    if ip is not None:
                        if len(ip) == 2:  # One piece intersection points
                            if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                            else:
                                r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                            intersection_points[count].add(r_ip)  # Add to set
                        elif len(ip) == 4:  # Overlapping sections
                            if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                            else:
                                r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                            for i in range(0, len(r_ip) - 1, 2):
                                intersection_points[count].add((r_ip[i], r_ip[i + 1]))  # Add to set

    # set to list conversion
    intersection_points = [list(ips) for ips in intersection_points]
    if angle_degrees >= 0 and angle_degrees < 90:
        sorted_intersection_points = [sorted(row, key=lambda point: (point[0], -point[1])) for row in intersection_points]
    elif angle_degrees >= 90 and angle_degrees < 180:
        sorted_intersection_points = [sorted(row, key=lambda point: (-point[0], -point[1])) for row in intersection_points]
    elif angle_degrees >= 180 and angle_degrees < 270:
        sorted_intersection_points = [sorted(row, key=lambda point: (-point[0], point[1])) for row in intersection_points]
    elif angle_degrees >= 270 and angle_degrees < 360:
        sorted_intersection_points = [sorted(row, key=lambda point: (point[0], point[1])) for row in intersection_points]
    return sorted_intersection_points

# Calculate intersection points between two segments       
def find_intersection_of_segments(segment1_f, segment1_e, segment2_f, segment2_e):
    # Start and end points of the first segment
    x1, y1 = segment1_f
    x2, y2 = segment1_e
    
    # Start and end points of the second segment
    x3, y3 = segment2_f
    x4, y4 = segment2_e
    
    # Direction vectors of the first and second segments
    dx1, dy1 = x2 - x1, y2 - y1
    dx2, dy2 = x4 - x3, y4 - y3

    # Solving a system of linear equations according to Cramer's rule
    denominator = dx1 * dy2 - dy1 * dx2  # Determinant

    # If denominator is 0, the segments are parallel or collinear
    if abs(denominator) < 1e-6:  # Increased tolerance for parallel segments
        # Check for collinearity
        collinear_check = (y2 - y1) * (x3 - x1) == (x2 - x1) * (y3 - y1)
        
        if collinear_check:
            # Find overlap in the x and y ranges with a slightly higher tolerance
            overlap_x1 = max(min(x1, x2), min(x3, x4))
            overlap_x2 = min(max(x1, x2), max(x3, x4))
            overlap_y1 = max(min(y1, y2), min(y3, y4))
            overlap_y2 = min(max(y1, y2), max(y3, y4))
            if overlap_x1 <= overlap_x2 and overlap_y1 <= overlap_y2:  # Check if there is a valid overlap
                # Return the overlapping segment
                return (overlap_x1, overlap_y1, overlap_x2, overlap_y2)
        return None  # Parallel, no intersection
    
    # According to Cramer's rule
    numerator_t = (x3 - x1) * dy2 - (y3 - y1) * dx2
    numerator_u = (x3 - x1) * dy1 - (y3 - y1) * dx1
    
    t = numerator_t / denominator
    u = numerator_u / denominator

    # Check if the intersection point is within both segments (0 <= t, u <= 1) with adjusted epsilon
    epsilon = 1e-6  # Adjusted tolerance limit
    if -epsilon <= t <= 1 + epsilon and -epsilon <= u <= 1 + epsilon:
        # The coordinate of the point of intersection
        intersection_x = x1 + t * dx1
        intersection_y = y1 + t * dy1
        return (intersection_x, intersection_y)
    else:
        return None  # There is no intersection between the two segments

    

#Deleting bad intersection points when not in coordinate points
def deleting_bad_intersection_points(intersection_points, n_coordinate_points):
    del_ip = []
    for ip in range(len(intersection_points)):
        for idx in range(len(intersection_points[ip])):
            in_coordinate_points = np.where((n_coordinate_points == intersection_points[ip][idx]).all(axis=1))[0]
            if in_coordinate_points.size == 0:
                del_ip.append([ip, idx])

    for row, idx in sorted(del_ip, reverse=True):
        del intersection_points[row][idx]

#Searching good lines between intersection points
def selecting_good_lines(intersection_points, b_lines, robot_size, n_internal_coordinate_points_of_obstacle, n_outside_of_map, n_coordinate_points):
    finally_b_lines = [[] for _ in range(len(b_lines))]
    for count, ip in enumerate(intersection_points):
        if len(ip) == 0:
            continue
        for i in range(len(ip) - 1):
            dist = calculate_distance(ip[i], ip[i + 1]) 
            if dist > robot_size:
                line = bresenham(ip[i][0], ip[i][1], ip[i + 1][0], ip[i + 1][1])
                n_line = np.array(line)
                if n_line.size > 0:
                    line_is_good = True
                    for  l in range(len(n_line)):
                        in_obstacle = np.where((n_internal_coordinate_points_of_obstacle == n_line[l]).all(axis=1))[0]
                        in_outside = np.where((n_outside_of_map == n_line[l]).all(axis=1))[0]
                        if in_obstacle.size != 0 or in_outside.size != 0:
                            line_is_good = False
                            break
                    if line_is_good: 
                        for ll in range(len(n_line)):
                            in_coordinate = np.where((n_coordinate_points == n_line[ll]).all(axis=1))[0]
                            if in_coordinate.size == 0:
                                finally_b_lines[count].append(n_line)
                                break
    return finally_b_lines

# Draw lines in map
def draw_lines(points, color):
    for pt in points:
        if pt == []:
            continue
        else:
            for p in range(0,len(pt) - 1, 2):
                plt.plot((pt[p][0], pt[p + 1][0]), (pt[p][1], pt[p + 1][1]), color=color, linewidth=1)

# Calculate list depth
def get_list_depth(lst, depth=0):
    if isinstance(lst, list):
        return max(get_list_depth(item, depth + 1) for item in lst) if lst else depth
    
    return depth
