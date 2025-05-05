import numpy as np
import math
import sys
import copy

# save_map_and_obstacle_boundaries.py

SQUARE_ROOR_2 = math.sqrt(2)

def deep_swap(array, index1, index2):
    temp = copy.deepcopy(array[index1]) 
    array[index1] = copy.deepcopy(array[index2])  
    array[index2] = temp  

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
    for shape_c in shape_coordinates:
        for sc in range(len(shape_c) - 1, 0, -1):
            if len(shape_c[sc]) == 1:
                for idx in range(sc - 1, 0, -1):
                    dist1 = calculate_distance(shape_c[sc][0], shape_c[idx][0])
                    dist2 = calculate_distance(shape_c[sc][0], shape_c[idx][-1])
                    if dist1 < 1.42:
                        shape_c[idx] = np.vstack([shape_c[sc], shape_c[idx]])
                        to_remove.append(sc)
                        break
                    elif dist2 < 1.42:
                        to_remove.append(sc)
                        break
                    elif idx == 1:
                        to_remove.append(sc)

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
        for shape_c in range(len(shape_coordinates) - 1):
            start_x_y = shape_coordinates[shape_c][0]
            end_x_y = shape_coordinates[shape_c][-1]
            for sc in range(shape_c + 1, len(shape_coordinates)):
                other_start_x_y = shape_coordinates[sc][0]
                other_end_x_y = shape_coordinates[sc][-1]

                # Calculate distances
                dist1 = calculate_distance(start_x_y, other_start_x_y)
                dist2 = calculate_distance(start_x_y, other_end_x_y)
                dist3 = calculate_distance(end_x_y, other_end_x_y)
                dist4 = calculate_distance(end_x_y, other_start_x_y)

                # Check if merging is possible and append indexes
                if dist1 <= SQUARE_ROOR_2:
                    indexes.append(['dist1', shape_c, sc])
                if dist2 <= SQUARE_ROOR_2:
                    indexes.append(['dist2', shape_c, sc])
                if dist3 <= SQUARE_ROOR_2:
                    indexes.append(['dist3', shape_c, sc])
                if dist4 <= SQUARE_ROOR_2:
                    indexes.append(['dist4', shape_c, sc])

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
        for sc in range(len(shape_coordinates)):
            first_coord = shape_coordinates[sc][0]
            last_coord = shape_coordinates[sc][-1]
            dist = calculate_distance(first_coord, last_coord)
            if dist <= SQUARE_ROOR_2:
                shape_coordinates[sc] = np.vstack((shape_coordinates[sc], first_coord))
                shapes.extend([shape_coordinates[sc]])
                del_shapes.append(sc)
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
    for sc in range(len(shape_coordinates)):
        first_coord = shape_coordinates[sc][0]
        last_coord = shape_coordinates[sc][-1]
        dist = calculate_distance(first_coord, last_coord)
        if dist <= SQUARE_ROOR_2:
            shape_coordinates[sc] = np.vstack((shape_coordinates[sc], first_coord))
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
    is_empty = len(shape_coordinates) == 0
    ok_shape = True
    for s in shapes:
        if not np.array_equal(s[0], s[-1]):
            ok_shape = False

    if is_empty and ok_shape:
       print('All shapes were detected!')
    else:
        print('Not all shapes were detected!')
        sys.exit("Exiting program: shape detection failed.")