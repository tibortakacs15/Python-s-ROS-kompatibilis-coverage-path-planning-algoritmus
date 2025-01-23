 import numpy as np
import math
import matplotlib.pyplot as plt

# calculate_intersection_points.py

# Convert RGB to grayscale manually
def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

# Calculate edges coordinates points
def calculate_edges_coordinates(labeled_edges, number):
    coordinate_points = []
    if number > 2:
        for n in range(3, number, 1):
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
    """Convert an angle in degrees to the slope of a line."""
    radians = np.radians(degrees)
    return np.tan(radians)

def draw_parallel_lines_with_angle(image, angle_degrees, spacing, scale_factor, min_max_x_y_coord):
    height, width = image.shape[:2]
    
    # Angle degree conver to radian
    angle_radians = math.radians(angle_degrees)
    
    # Calculating an offset perpendicular to the direction of a line
    offset_x = spacing * math.sin(angle_radians)
    offset_y = spacing * math.cos(angle_radians)
    
    # Calculating the start and end points of a baseline
    if 0 <= angle_degrees < 90:
        start_x, start_y = 0, height  # bal alsó sarok
        end_x = width
        end_y = height - width * math.tan(angle_radians)
    elif 90 <= angle_degrees < 180:
        start_x, start_y = width, height  # jobb alsó sarok
        end_x = width + height / math.tan(angle_radians)
        end_y = 0
    elif 180 <= angle_degrees < 270:
        start_x, start_y = width, 0  # jobb felső sarok
        end_x = 0
        end_y = width * math.tan(angle_radians - math.pi)
    else:
        start_x, start_y = 0, 0  # bal felső sarok
        end_x = height / math.tan(math.pi * 2 - angle_radians)
        end_y = height

 # Apply scaling to start and end points
    center_x = (start_x + end_x) / 2
    center_y = (start_y + end_y) / 2
    start_x = center_x + (start_x - center_x) * scale_factor
    start_y = center_y + (start_y - center_y) * scale_factor
    end_x = center_x + (end_x - center_x) * scale_factor
    end_y = center_y + (end_y - center_y) * scale_factor

    # Calculating number of lines
    if width > height:
        num_lines = int(width / spacing)
    else :
        num_lines = int(height / spacing)
    lines = []
    for i in range(-num_lines, num_lines):
        line = []
        # Shifting the start and end points
        line_start_x = start_x + i * offset_x
        line_start_y = start_y + i * offset_y
        line_end_x = end_x + i * offset_x
        line_end_y = end_y + i * offset_y

        # Good line that intersects the map
        intersection1 = find_intersection_of_segments([min_max_x_y_coord[0], min_max_x_y_coord[1]], [min_max_x_y_coord[2], min_max_x_y_coord[3]], [line_start_x, line_start_y], [line_end_x, line_end_y])
        intersection2 = find_intersection_of_segments([min_max_x_y_coord[0], min_max_x_y_coord[3]], [min_max_x_y_coord[2], min_max_x_y_coord[1]], [line_start_x, line_start_y], [line_end_x, line_end_y])
        if intersection1 != None or intersection2 != None:
            line.append(np.array([line_start_x, line_start_y])) 
            line.append(np.array([line_end_x, line_end_y]))
            lines.append(line)
    return lines

#  The shape points located between parallel lines
def edges_of_the_shapes(lines, n_coordinate_points, angle_degrees):
    edge_coordinates  = []
    for l in range(len(lines)):
        if angle_degrees <= 180:
            end, start = lines[l][0][1], lines[l][1][1] # paralell lines start and end points
        elif angle_degrees > 180:
            start, end = lines[l][0][1], lines[l][1][1] # paralell lines start and end points
        start = int(math.floor(start))
        end = int(math.ceil(end))
        condition = (n_coordinate_points[:, 1] >= start) & (n_coordinate_points[:, 1] <= end)  
        result = n_coordinate_points[condition]
        edge_coordinates.append(result)
    return edge_coordinates

# Function to calculate the Euclidean distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

# 
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
    is_merging = True
    while is_merging:
        indexes = [] 
        for sh in range(len(shape_coordinates) - 1):
            start_x_y = shape_coordinates[sh][0]
            end_x_y = shape_coordinates[sh][-1]
            for s in range(sh + 1, len(shape_coordinates)):
                other_start_x_y = shape_coordinates[s][0]
                other_end_x_y = shape_coordinates[s][-1]
                dist1 = calculate_distance(start_x_y, other_start_x_y)
                dist2 = calculate_distance(start_x_y, other_end_x_y)
                dist3 = calculate_distance(end_x_y, other_end_x_y)
                dist4 = calculate_distance(end_x_y, other_start_x_y)
                if dist1 < 1.42:
                    indexes.extend([['dist1', sh, s]])
                if dist2 < 1.42:
                    indexes.extend([['dist2', sh, s]])
                if dist3 < 1.42:
                    indexes.extend([['dist3', sh, s]])
                if dist4 < 1.42:
                    indexes.extend([['dist4', sh, s]])
            sorted_indexes = sorted(indexes, key=lambda x: x[2], reverse=True)
            
        unique_indexes = []
        seen_third_elements = set()
        for item in sorted_indexes:
            if item[2] not in seen_third_elements:
                unique_indexes.append(item)
                seen_third_elements.add(item[2])
        for un_idx in range(len(unique_indexes)):
            if unique_indexes[un_idx][0] == 'dist1':
                shape_coordinates[unique_indexes[un_idx][2]][:] = shape_coordinates[unique_indexes[un_idx][2]][::-1]
                shape_coordinates[unique_indexes[un_idx][1]] = np.vstack([shape_coordinates[unique_indexes[un_idx][2]], shape_coordinates[unique_indexes[un_idx][1]]])
            elif unique_indexes[un_idx][0] == 'dist2':
                shape_coordinates[unique_indexes[un_idx][1]] = np.vstack([shape_coordinates[unique_indexes[un_idx][2]], shape_coordinates[unique_indexes[un_idx][1]]])
            elif unique_indexes[un_idx][0] == 'dist3':
                shape_coordinates[unique_indexes[un_idx][2]][:] = shape_coordinates[unique_indexes[un_idx][2]][::-1]
                shape_coordinates[unique_indexes[un_idx][1]] = np.vstack([shape_coordinates[unique_indexes[un_idx][1]], shape_coordinates[unique_indexes[un_idx][2]]])
            elif unique_indexes[un_idx][0] == 'dist4':
                shape_coordinates[unique_indexes[un_idx][1]] = np.vstack([shape_coordinates[unique_indexes[un_idx][1]], shape_coordinates[unique_indexes[un_idx][2]]])
        if len(unique_indexes) > 0:  
            for un_idx in range(len(unique_indexes)):
                del (shape_coordinates[unique_indexes[un_idx][2]])
        else: 
            is_merging = False
    for s in range(len(shape_coordinates)):
        first_coord = shape_coordinates[s][0]
        last_coord = shape_coordinates[s][-1]
        dist = calculate_distance(first_coord, last_coord)
        if dist < 1.42:
            shape_coordinates[s] = np.vstack((shape_coordinates[s], first_coord))

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
    if abs(denominator) < 1e-9:  
        # Check for collinearity
        if (y2 - y1) * (x3 - x1) == (x2 - x1) * (y3 - y1):  # Collinear check
            # Find overlap in the x and y ranges
            overlap_x1 = max(min(x1, x2), min(x3, x4))
            overlap_x2 = min(max(x1, x2), max(x3, x4))
            overlap_y1 = max(min(y1, y2), min(y3, y4))
            overlap_y2 = min(max(y1, y2), max(y3, y4))

            if overlap_x1 <= overlap_x2 and overlap_y1 <= overlap_y2:  # Check if there is a valid overlap
                # Return the overlapping segment
                return (overlap_x1, overlap_y1, overlap_x2, overlap_y2)
        return None  # Parallel, no intersection
    
    # Cramer-szabály szerinti megoldás a t és u paraméterekre
    numerator_t = (x3 - x1) * dy2 - (y3 - y1) * dx2
    numerator_u = (x3 - x1) * dy1 - (y3 - y1) * dx1
    
    t = numerator_t / denominator
    u = numerator_u / denominator
   
    # Check if the intersection point is within both segments (0 <= t, u <= 1)
    epsilon = 1e-9  # Tolerance limit
    if -epsilon <= t <= 1 + epsilon and -epsilon <= u <= 1 + epsilon:
        # The coordinate of the point of intersection
        intersection_x = x1 + t * dx1
        intersection_y = y1 + t * dy1
        return (intersection_x, intersection_y)
    else:
        return None  # There is no intersection between the two segments



# Calculate intersection points by shape coordinates and lines
def calculate_intersection_points(shape_coordinates, n_coordinate_points, n_internal_coordinate_points_of_barrier, lines, angle_degrees):
    intersection_points = [[] for _ in range(len(lines))]
    for idx in range(len(shape_coordinates)):
        ec = edges_of_the_shapes(lines, shape_coordinates[idx], angle_degrees)
        for count, (e, l) in enumerate(zip(ec, lines)):
            if len(e) == 0:
                continue
            else:
                for i in range(len(e) - 1):
                    ip = find_intersection_of_segments( e[i],  e[i + 1], l[0], l[1])
                    
                    if ip != None:
                        if len(ip) == 2:
                            good_ip = good_intersection_point(n_coordinate_points, n_internal_coordinate_points_of_barrier, ip, angle_degrees, 1)
                            if good_ip:
                             intersection_points[count].append(ip)
                        elif len(ip) == 4:
                            for i in range(0, len(ip) - 1, 2):
                                good_ip = good_intersection_point(n_coordinate_points, n_internal_coordinate_points_of_barrier, [ip[i], ip[i + 1]], angle_degrees, 1)
                                if good_ip:
                                    intersection_points[count].append((ip[i], ip[i + 1]))
    # List converted to set due to duplicate points
    set_intersection_points = [set(row) for row in intersection_points]
    new_intersection_points = [list(row) for row in set_intersection_points]

    sorted_intersection_points = [sorted(row, key=lambda point: point[0]) for row in new_intersection_points]
    return sorted_intersection_points

def good_intersection_point(n_coordinate_points, n_internal_coordinate_points_of_barrier, ip, angle_deg, d):
    angle_rad = math.radians(angle_deg) 
    # Offset point by distance d
    dx = (-d) * math.cos(angle_rad)
    dy = (-d) * math.sin(angle_rad)

    b_x_new = ip[0] + dx
    b_y_new = ip[1] + dy

    dx = d * math.cos(angle_rad)
    dy = d * math.sin(angle_rad)

    a_x_new = ip[0] + dx
    a_y_new = ip[1] + dy

    talalat1 = np.where((n_coordinate_points == [a_x_new, a_y_new]).all(axis=1))[0]
    talalat2 = np.where((n_coordinate_points == [b_x_new, b_y_new]).all(axis=1))[0]
    talalat3 = np.where((n_internal_coordinate_points_of_barrier == [a_x_new, a_y_new]).all(axis=1))[0]
    talalat4 = np.where((n_internal_coordinate_points_of_barrier == [b_x_new, b_y_new]).all(axis=1))[0]
    
    if (talalat1.size != 0 and talalat2.size != 0) or (talalat2.size != 0 and talalat3.size != 0) or (talalat1.size != 0 and talalat4.size != 0):
        return False
    else:
        return True

# Cut line by robot size
def cut_line_segment(x1, y1, x2, y2, d):
    # Calculate direction vector
    vx, vy = x2 - x1, y2 - y1
    # Calculate length of the vector
    h = math.sqrt(vx**2 + vy**2)
    # if h smaler then distence return empty tuple
    if h <= d:
        return ()
    # Calculate unit vector
    ux, uy = vx / h, vy / h
    # Calculate new start and end points
    x1_new, y1_new = x1 + d * ux, y1 + d * uy
    x2_new, y2_new = x2 - d * ux, y2 - d * uy
    return (x1_new, y1_new, x2_new, y2_new)


