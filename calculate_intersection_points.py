import numpy as np
import matplotlib.pyplot as plt
import math
import copy

# calculate_intersection_points.py

SQUARE_ROOR_2 = math.sqrt(2)

def deep_swap(array, index1, index2):
    temp = copy.deepcopy(array[index1]) 
    array[index1] = copy.deepcopy(array[index2])  
    array[index2] = temp  

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

# Calculating the degree by slope
def degrees_to_slope(degrees):
    radians = np.radians(degrees)
    return np.tan(radians)

def draw_parallel_lines_with_angle(image, min_max_x_y_coord, angle_degrees, robot_size, scale_factor):
    height, width = image.shape[:2]
    spacing = robot_size // 2
    
    # Angle degree to radian
    angle_radians = math.radians(angle_degrees)
    
    # Special cases for 0°, 90°, 180°, 270°
    if angle_degrees == 0:
        offset_x, offset_y = 0, spacing
    elif angle_degrees == 90:
        offset_x, offset_y = spacing, 0
    elif angle_degrees == 180:
        offset_x, offset_y = 0, -spacing
    elif angle_degrees == 270:
        offset_x, offset_y = -spacing, 0
    else:
        offset_x = spacing * math.sin(angle_radians)
        offset_y = spacing * math.cos(angle_radians)
    
    # Calculate baseline start and end points
    if angle_degrees == 0:
        start_x, start_y = 0, height
        end_x, end_y = width, height
    elif angle_degrees == 90:
        start_x, start_y = 0, 0
        end_x, end_y = 0, height
    elif angle_degrees == 180:
        start_x, start_y = width, 0
        end_x, end_y = 0, 0
    elif angle_degrees == 270:
        start_x, start_y = width, height
        end_x, end_y = width, 0
    else:
        start_x, start_y = 0, height
        end_x = width
        end_y = height - width * math.tan(angle_radians)
    
    # Apply scaling
    center_x = (start_x + end_x) / 2
    center_y = (start_y + end_y) / 2
    start_x = center_x + (start_x - center_x) * scale_factor
    start_y = center_y + (start_y - center_y) * scale_factor
    end_x = center_x + (end_x - center_x) * scale_factor
    end_y = center_y + (end_y - center_y) * scale_factor
    
    # Generate lines
    num_lines = max(width, height) // (spacing // 2)
    lines = []
    for i in range(-num_lines, num_lines + 1):
        line_start_x = start_x + i * offset_x
        line_start_y = start_y + i * offset_y
        line_end_x = end_x + i * offset_x
        line_end_y = end_y + i * offset_y
        
        clipped_line = liang_barsky_clip(line_start_x, line_start_y, line_end_x, line_end_y, min_max_x_y_coord)
        if clipped_line:
            lines.append([
                np.array([round(clipped_line[0]), round(clipped_line[1])]),
                np.array([round(clipped_line[2]), round(clipped_line[3])])
            ])
       
    return lines

# Keeps the value within the allowed range
def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value, )

# Liang-Barsky algorithm for cutting lines within an image frame.
def liang_barsky_clip(x1, y1, x2, y2, min_max_x_y_coord):
    x_min = min_max_x_y_coord[0]
    y_min  = min_max_x_y_coord[1]
    x_max = min_max_x_y_coord[2]
    y_max = min_max_x_y_coord[3]
    
    def clip(p, q, t0, t1):
        if p == 0:  # With parallel edge
            return (t0, t1) if q >= 0 else (None, None)
        t = q / p
        if p < 0:
            if t > t1:
                return None, None
            if t > t0:
                t0 = t
        else:
            if t < t0:
                return None, None
            if t < t1:
                t1 = t
        return t0, t1

    dx = x2 - x1
    dy = y2 - y1
    t0, t1 = 0, 1

    t0, t1 = clip(-dx, x1 - x_min, t0, t1)
    if t0 is None: return None
    t0, t1 = clip(dx, x_max - x1, t0, t1)
    if t0 is None: return None
    t0, t1 = clip(-dy, y1 - y_min, t0, t1)
    if t0 is None: return None
    t0, t1 = clip(dy, y_max - y1, t0, t1)
    if t0 is None: return None

    new_x1 = x1 + t0 * dx
    new_y1 = y1 + t0 * dy
    new_x2 = x1 + t1 * dx
    new_y2 = y1 + t1 * dy

    return round(new_x1), round(new_y1), round(new_x2), round(new_y2)

# Bresenham's algorithms 
def bresenham(x1, y1, x2, y2):
    points = []
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    while True:
        points.append((x1, y1))
        
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    
    return np.array(points)

# Cuts the line to the edges of the picture frame and then calculates the points with Bresenham.
def clip_and_draw_line(start_x, start_y, end_x, end_y, min_max_x_y_coord):
    x_min, y_min, x_max, y_max = min_max_x_y_coord
    
    # Cut the line first
    clipped = liang_barsky_clip(start_x, start_y, end_x, end_y, x_min, y_min, x_max, y_max)
    
    if clipped is None:
        return np.array([]) # If the line is completely outside, return with an empty list

    x1, y1, x2, y2 = clipped

    # Calculates points using Bresenham algorithm
    return bresenham(x1, y1, x2, y2)

#  The shape points located between parallel lines
def edges_of_the_shapes(lines, n_coordinate_points, angle_degrees):
    edge_coordinates  = []
    if angle_degrees <= 180:
        end, start = lines[0][1], lines[-1][1] # paralell lines start and end points
    elif angle_degrees > 180:
        start, end = lines[0][1], lines[-1][1] # paralell lines start and end points
    condition = (n_coordinate_points[:, 1] >= start) & (n_coordinate_points[:, 1] <= end)  
    result = n_coordinate_points[condition]
    edge_coordinates.append(result)
    return edge_coordinates

# Function to calculate the Euclidean distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def connecting_the_points(edge_coordinates):
    segment = []
    
    # We go through all the points
    for ec in edge_coordinates:  
        found_segment = False
        potential_segment_index = None  # Here we store the index of the segment with a distance of 1.41421
        
        # The current point can be added to a segment
        for s in range(len(segment)):
            dist = calculate_distance(segment[s][-1], ec)
            
            # The distance is 1 the point is added to the segment
            if dist == 1:
                segment[s] = np.vstack([segment[s], ec])
                found_segment = True
                break
            
            # The distance close to 1.41421 is stored but not yet added
            elif dist < 1.42 and potential_segment_index is None:
                potential_segment_index = s
        
        # Did not find distance 1, but there was a distance of 1.4142, a point can be added to the segment
        if not found_segment and potential_segment_index is not None:
            segment[potential_segment_index] = np.vstack([segment[potential_segment_index], ec])
            found_segment = True

        # Did not find distance 1 or distance 1.4142, create a new segment
        if not found_segment:
            segment.append(np.array([ec]))

    return segment

# If the segment has a point, insert into another segment and delete the segment
def insert_and_remove_one_coordinate_array(shape_coordinates):
    to_remove = []
    for sc in shape_coordinates:
        for s in range(len(sc) - 1, 0, -1):
            if len(sc[s]) == 1:
                for idx in range(s - 1, 0, -1):
                    dist1 = calculate_distance(sc[s][0], sc[idx][0])
                    dist2 = calculate_distance(sc[s][0], sc[idx][-1])
                    if dist1 < 1.42:
                        sc[idx] = np.vstack([sc[s], sc[idx]])
                        to_remove.append(s)
                        break
                    elif dist2 < 1.42:
                        to_remove.append(s)
                        break
                    elif idx == 1:
                        to_remove.append(s)

    for idx in sorted(to_remove, reverse=True):
        del shape_coordinates[0][idx]

# Merge segments by distance
def merge_segments(shape_coordinates):
    if len(shape_coordinates) == 0:
        return 0  # Exit with 0 instead of returning 'exit'

    is_merging = True
    while is_merging:
        indexes = []
        
        # Populate 'indexes' with merge candidates
        for sh in range(len(shape_coordinates) - 1):
            start_x_y = shape_coordinates[sh][0]
            end_x_y = shape_coordinates[sh][-1]
            for s in range(sh + 1, len(shape_coordinates)):
                other_start_x_y = shape_coordinates[s][0]
                other_end_x_y = shape_coordinates[s][-1]

                # Calculate distances
                dist1 = calculate_distance(start_x_y, other_start_x_y)
                dist2 = calculate_distance(start_x_y, other_end_x_y)
                dist3 = calculate_distance(end_x_y, other_end_x_y)
                dist4 = calculate_distance(end_x_y, other_start_x_y)

                # Check if merging is possible and append indexes
                if dist1 <= SQUARE_ROOR_2:
                    indexes.append(['dist1', sh, s])
                if dist2 <= SQUARE_ROOR_2:
                    indexes.append(['dist2', sh, s])
                if dist3 <= SQUARE_ROOR_2:
                    indexes.append(['dist3', sh, s])
                if dist4 <= SQUARE_ROOR_2:
                    indexes.append(['dist4', sh, s])

        # Initialize sorted_indexes to avoid UnboundLocalError
        sorted_indexes = []
        if len(indexes) > 0:
            sorted_indexes = sorted(indexes, key=lambda x: x[2], reverse=True)
        if len(sorted_indexes) > 0:
            # Filter unique indexes
            unique_indexes = []
            seen_third_elements = set()
            for item in sorted_indexes:
                if item[2] not in seen_third_elements:
                    unique_indexes.append(item)
                    seen_third_elements.add(item[2])

            # Perform the merging process
            for un_idx in range(len(unique_indexes)):
                dist_type, idx1, idx2 = unique_indexes[un_idx]
                if dist_type == 'dist1':
                    shape_coordinates[idx2][:] = shape_coordinates[idx2][::-1]
                    shape_coordinates[idx1] = np.vstack([shape_coordinates[idx2], shape_coordinates[idx1]])
                elif dist_type == 'dist2':
                    shape_coordinates[idx1] = np.vstack([shape_coordinates[idx2], shape_coordinates[idx1]])
                elif dist_type == 'dist3':
                    shape_coordinates[idx2][:] = shape_coordinates[idx2][::-1]
                    shape_coordinates[idx1] = np.vstack([shape_coordinates[idx1], shape_coordinates[idx2]])
                elif dist_type == 'dist4':
                    shape_coordinates[idx1] = np.vstack([shape_coordinates[idx1], shape_coordinates[idx2]])

            # Delete merged shapes
            for un_idx in range(len(unique_indexes)):
                del shape_coordinates[unique_indexes[un_idx][2]]
        else:
            is_merging = False  # No more merges possible
    return 0

# Moving perfect shapes in  new array
def perfect_shapes(shape_coordinates):
    del_shapes = []
    shapes = []
    if len(shape_coordinates) > 0:
        for s in range(len(shape_coordinates)):
            first_coord = shape_coordinates[s][0]
            last_coord = shape_coordinates[s][-1]
            dist = calculate_distance(first_coord, last_coord)
            if dist <= SQUARE_ROOR_2:
                shape_coordinates[s] = np.vstack((shape_coordinates[s], first_coord))
                shapes.extend([shape_coordinates[s]])
                del_shapes.append(s)
        sort_del_shape = sorted(del_shapes, reverse=True)
        if len(sort_del_shape) > 0:  
                for ds_idx in range(len(sort_del_shape)):
                    del (shape_coordinates[sort_del_shape[ds_idx]])
    return shapes

# Checking start and end points in arrays
def checking_start_and_end_points1(shape_coordinates):
    if len(shape_coordinates) == 0:
        return False
    is_change = False
    for s in range(len(shape_coordinates)):
        first_coord = shape_coordinates[s][0]
        last_coord = shape_coordinates[s][-1]
        dist = calculate_distance(first_coord, last_coord)
        if dist <= SQUARE_ROOR_2:
            shape_coordinates[s] = np.vstack((shape_coordinates[s], first_coord))
        else:
            for sublist in shape_coordinates:
                if len(sublist) > 6:
                    dist1 = calculate_distance(sublist[0], sublist[1])
                    dist2 = calculate_distance(sublist[1], sublist[2])
                    dist3 = calculate_distance(sublist[0], sublist[2])
                    dist4 = calculate_distance(sublist[0], sublist[3])
                   
                    if (dist1 == 1 and dist2 == 1 and dist3 == SQUARE_ROOR_2 and dist4 == 2):
                        deep_swap(sublist, 0, 1)
                        deep_swap(sublist, 0, 2)
                        is_change = True
                    elif dist1 == 1 and dist2 == SQUARE_ROOR_2 and dist3 == 1:
                        deep_swap(sublist, 0, 1)
                        is_change = True
            
            for sublist in shape_coordinates:
                 if len(sublist) > 6:
                    dist1 = calculate_distance(sublist[-1], sublist[-2])
                    dist2 = calculate_distance(sublist[-2], sublist[-3])
                    dist3 = calculate_distance(sublist[-1], sublist[-3])
                    dist4 = calculate_distance(sublist[-1], sublist[-4])
                    
                    if dist1 == 1 and dist2 == 1 and dist3 == SQUARE_ROOR_2 and dist4 == 2:
                        deep_swap(sublist, -1,-2)
                        deep_swap(sublist, -1, -3)
                        is_change = True
                    elif dist1 == 1 and dist2 == SQUARE_ROOR_2 and dist3 == 1:
                        deep_swap(sublist, -1, -2)
                        is_change = True
                        
    return is_change

# Checking start and end points in arrays
def checking_start_and_end_points2(shape_coordinates):
    if len(shape_coordinates) == 0:
        return False
    is_change = False
    for s in range(len(shape_coordinates)):
        first_coord = shape_coordinates[s][0]
        last_coord = shape_coordinates[s][-1]
        dist = calculate_distance(first_coord, last_coord)
        if dist <= SQUARE_ROOR_2:
            shape_coordinates[s] = np.vstack((shape_coordinates[s], first_coord))
        else:
            for sublist in shape_coordinates:
                if len(sublist) > 6:
                    dist1 = calculate_distance(sublist[0], sublist[1])
                    dist2 = calculate_distance(sublist[1], sublist[2])
                    dist3 = calculate_distance(sublist[0], sublist[2])
                    if dist1 == 1 and dist2 == 1 and dist3 == SQUARE_ROOR_2:
                        deep_swap(sublist, 0, 1)
                        is_change  = True
            for sublist in shape_coordinates:
                 if len(sublist) > 6:
                    dist1 = calculate_distance(sublist[-1], sublist[-2])
                    dist2 = calculate_distance(sublist[-2], sublist[-3])
                    dist3 = calculate_distance(sublist[-1], sublist[-3])
                    if dist1 == 1 and dist2 == 1 and dist3 == SQUARE_ROOR_2:
                        deep_swap(sublist, -1, -2)
                        is_change  = True
                       
    return is_change 

def result_detection(shape_coordinates, shapes):
    if len(shape_coordinates) == 0:
        is_empty = True
    ok_shape = True
    for s in shapes:
        if not np.array_equal(s[0], s[-1]):
            ok_shape = False

    if is_empty and ok_shape:
        print('The all shapes will detectation!')
    else:
        print('Does not detect all shapes!')

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
                            for i in range(0, len(ip) - 1, 2):
                                intersection_points[count].add((ip[i], ip[i + 1]))  # Add to set

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
def selecting_good_lines(intersection_points, b_lines, robot_size, n_internal_coordinate_points_of_barrier, n_outside_of_map, n_coordinate_points):
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
                        in_barrier = np.where((n_internal_coordinate_points_of_barrier == n_line[l]).all(axis=1))[0]
                        in_outside = np.where((n_outside_of_map == n_line[l]).all(axis=1))[0]
                        if in_barrier.size != 0 or in_outside.size != 0:
                            line_is_good = False
                            break
                    if line_is_good: 
                        for ll in range(len(n_line)):
                            in_coordinate = np.where((n_coordinate_points == n_line[ll]).all(axis=1))[0]
                            if in_coordinate.size == 0:
                                finally_b_lines[count].append(n_line)
                                break
    return finally_b_lines

# Cut line by robot size
def trim_line(points, robot_size):
    size = robot_size // 2
    if len(points) <= 2 * size:
        return np.array([])  # If the line is too short deleting

    return points[size:-size]  # Cuts off the beginning and end

def draw_bresenham_lines(b_lines, color):
    for lines in b_lines:
        for line in lines:
            if len(line) == 0:
                continue
            x = line[:, 0]  # X coordinates
            y = line[:, 1]  # Y coordinates
            plt.plot(x, y, color=color)  

# Draw lines in map
def draw_lines(points, color):
    for pt in points:
        if pt == []:
            continue
        else:
            for p in range(0,len(pt) - 1, 2):
                plt.plot((pt[p][0], pt[p + 1][0]), (pt[p][1], pt[p + 1][1]), color=color, linewidth=1)
