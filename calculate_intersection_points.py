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
    spacing = robot_size

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
    x_min = min_max_x_y_coord[0] - 1
    y_min  = min_max_x_y_coord[1] - 1
    x_max = min_max_x_y_coord[2] + 1
    y_max = min_max_x_y_coord[3] + 1
    
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



# Calculate list depth
def get_list_depth(lst, depth=0):
    if isinstance(lst, list):
        return max(get_list_depth(item, depth + 1) for item in lst) if lst else depth
    return depth

def calculate_intersection_points_with_bresenham(shapes, square_lines, angle_degrees):
    intersection_points = []  

    for square_line in square_lines:
        square_intersections = []  

        for squ_line in square_line:
            all_intersections = set()  

            for s_line in squ_line:
                s_line_intersections = set()  

                for shape in shapes:
                    for s_l in range(len(s_line) - 1):
                        for sh in range(len(shape) - 1):
                            ip = find_intersection_of_segments(
                                shape[sh], shape[sh + 1], 
                                s_line[s_l], s_line[s_l + 1]
                            )

                            if ip is not None:
                                if len(ip) == 2:
                                    r_ip = (
                                        math.floor(ip[0]), math.floor(ip[1])
                                    ) if (0 <= angle_degrees < 90 or 180 <= angle_degrees < 270) else (
                                        math.ceil(ip[0]), math.floor(ip[1])
                                    )
                                    s_line_intersections.add(r_ip)

                                elif len(ip) == 4:
                                    for i in range(0, len(ip), 2):
                                        r_ip = (
                                            math.floor(ip[i]), math.floor(ip[i + 1])
                                        ) if (0 <= angle_degrees < 90 or 180 <= angle_degrees < 270) else (
                                            math.ceil(ip[i]), math.floor(ip[i + 1])
                                        )
                                        s_line_intersections.add(r_ip)

                all_intersections.update(s_line_intersections)

            sorted_intersections = sorted(all_intersections, key=lambda p: (p[0], p[1]))

            square_intersections.append(sorted_intersections if sorted_intersections else [])

        intersection_points.append(square_intersections)

    return intersection_points

def create_boundary_lines_on_the_sections(lines, robot_size):
    robot_size /= 2
    square_lines = [[] for _ in range(len(lines))]  

    for count, line_group in enumerate(lines): 
        for lg in line_group:
            if len(lg) == 0:
                square_lines[count].append([])
            else:
                s_lines = []
                x1, y1 = lg[0]
                x2, y2 = lg[-1]

                # Direction vector calculation
                dx, dy = x2 - x1, y2 - y1

                # Calculating a perpendicular vector (90 degree rotation)
                perp_x, perp_y = dy, -dx
                length = np.sqrt(perp_x**2 + perp_y**2)

                scale = robot_size / length
                dx, dy = perp_x * scale, perp_y * scale

                # Endpoints of a perpendicular line
                x1L, y1L = round(x1 + dx), round(y1 + dy)
                x1R, y1R = round(x1 - dx), round(y1 - dy)
                x2L, y2L = round(x2 + dx), round(y2 + dy)
                x2R, y2R = round(x2 - dx), round(y2 - dy)

                s_lines.extend([
                    [x1L, y1L, x2L, y2L],
                    [x2L, y2L, x2R, y2R],
                    [x2R, y2R, x1R, y1R],
                    [x1R, y1R, x1L, y1L]
                ])

                square_lines[count].append(s_lines) 

    return square_lines

def cut_start_and_end_points_bresenham_lines(b_lines, shapes, robot_size, angle_degrees):
    robot_size /= 2
    cut_lines = []
    for b_line in b_lines:
        if len(b_line) == 0:
            continue

        # Start point
        start_idx = int(robot_size) + 1
        is_ip = True
        while is_ip and len(b_line) > start_idx:
            if start_idx < len(b_line):
                x1, y1 = b_line[start_idx]  
                start_square = []
                xL1, yL1 = round(x1 - robot_size), round(y1 - robot_size)
                xR1, yR1 = round(x1 + robot_size), round(y1 + robot_size)
                start_square.extend([
                    [xL1, yL1, xR1, yL1],  # Top edge
                    [xR1, yL1, xR1, yR1],  # Right edge
                    [xR1, yR1, xL1, yR1],  # Bottom edge
                    [xL1, yR1, xL1, yL1]   # Left edge
                ])
                start_square_b_lines = []
                for ss in start_square:
                        s_s_b_lines = bresenham(ss[0], ss[1], ss[2], ss[3])  # Bresenham lines generation
                        start_square_b_lines.append(s_s_b_lines)
                intersection_points = set()
                for i in range(len(start_square_b_lines)): 
                    s_s_b_lines_1 = start_square_b_lines[i]      # First line set
                    for b_lines in range(0, len(s_s_b_lines_1) - 1):  # Lines within the first set
                        for shape in shapes: 
                            
                            for sh in range(0, len(shape) - 1):  
                                ip = find_intersection_of_segments(
                                    s_s_b_lines_1[b_lines], s_s_b_lines_1[b_lines + 1], 
                                    shape[sh], shape[sh + 1]
                                )
                                if ip is not None:
                                    if len(ip) == 2:  # One piece intersection points
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        intersection_points.add(r_ip)  # Add to set
                                    elif len(ip) == 4:  # Overlapping sections
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        for i in range(0, len(ip) - 1, 2):
                                            intersection_points.add((ip[i], ip[i + 1]))  # Add to set
                if len(intersection_points) > 0:
                    start_idx += 1
                elif len(intersection_points) == 0:
                    is_ip = False
            else:
               start_idx = len(b_line)

        # End point
        end_idx = int(-robot_size) - 2
        is_ip = True
        while is_ip and -(len(b_line)) < end_idx:
            if end_idx < len(b_line):
                x1, y1 = b_line[end_idx]  
                end_square = []
                xL1, yL1 = round(x1 - robot_size), round(y1 - robot_size)
                xR1, yR1 = round(x1 + robot_size), round(y1 + robot_size)
                end_square.extend([
                    [xL1, yL1, xR1, yL1],  # Top edge
                    [xR1, yL1, xR1, yR1],  # Right edge
                    [xR1, yR1, xL1, yR1],  # Bottom edge
                    [xL1, yR1, xL1, yL1]   # Left edge
                ])
                end_square_b_lines = []
                for ss in end_square:
                        s_s_b_lines = bresenham(ss[0], ss[1], ss[2], ss[3])  # Bresenham vonal generálása
                        end_square_b_lines.append(s_s_b_lines)

                intersection_points = set()
                for i in range(len(end_square_b_lines)):  # We go through it in pairs
                    s_s_b_lines_1 = end_square_b_lines[i]     
                    for b_lines in range(0, len(s_s_b_lines_1) - 1):  
                        for shape in shapes:  
                            
                            for sh in range(0, len(shape) - 1):  
                                ip = find_intersection_of_segments(
                                    s_s_b_lines_1[b_lines], s_s_b_lines_1[b_lines + 1], 
                                    shape[sh], shape[sh + 1]
                                )
                                if ip is not None:
                                        
                                    if len(ip) == 2:  # One piece intersection points
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        intersection_points.add(r_ip)  # Add to set
                                    elif len(ip) == 4:  # Overlapping sections
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        for i in range(0, len(ip) - 1, 2):
                                            intersection_points.add((ip[i], ip[i + 1]))  # Add to set
                if len(intersection_points) > 0:
                    end_idx -= 1
                elif len(intersection_points) == 0:
                    is_ip = False
            else:
                end_idx = len(b_line)
        # To get to the edge of the map, we subtract 1 from start_idx and add 1 to end_idx
        trimmed_points = b_line[start_idx:end_idx]
        if len(trimmed_points) > 1:
            cut_lines.append(trimmed_points)
    return cut_lines
    
def lines_convert_to_bresenham_lines(square_lines):
    b_s_lines = [[] for _ in range(len(square_lines))]

    for count, s_lines_group in enumerate(square_lines):  
        if not s_lines_group:  
            continue
        
        converted_group = []  
        
        for sl_group in s_lines_group:
            if len(sl_group) == 0:
                continue
            else:
                converted_sl_group = []  
                for slg in sl_group:
                    b_s_l = bresenham(slg[0], slg[1], slg[2], slg[3])  
                    converted_sl_group.append(b_s_l)
                
                converted_group.append(converted_sl_group)
        
        b_s_lines[count] = converted_group  

    return b_s_lines


def cut_bresenham_line_intersection_points(b_lines, intersections, angle_degrees):
    new_lines = []
    for (b_line, ips) in zip(b_lines, intersections):
        if len(b_line) == 0:
            continue  

        if len(ips) > 0:
            if (0 <= angle_degrees < 45) or (135 <= angle_degrees < 225) or (315 <= angle_degrees < 360):
                x = 0  
            elif (45 <= angle_degrees < 135) or (225 <= angle_degrees < 315):
                x = 1  

            sorted_points = sorted(set(p[x] for p in ips))  
            if not sorted_points:
                new_lines.append(b_line)
                continue

            x_or_y_value = set(p[x] for p in b_line)

            # Find the first and last valid intersection points on the line
            min_point = sorted_points[0]
            max_point = sorted_points[-1]

            for v in sorted_points:
                if v in x_or_y_value:
                    min_point = v
                    break 

            for v in reversed(sorted_points):
                if v in x_or_y_value:
                    max_point = v
                    break 

            # Cut a line based on min_point and max_point
            new_line1 = [bl for bl in b_line if bl[x] < min_point]
            new_line2 = [bl for bl in b_line if bl[x] > max_point]

            if len(new_line1) > 1:
                new_lines.append(new_line1)
            if len(new_line2) > 1:
                new_lines.append(new_line2)


        else:
            new_line = [bl for bl in b_line]
            new_lines.append(new_line)

    return new_lines