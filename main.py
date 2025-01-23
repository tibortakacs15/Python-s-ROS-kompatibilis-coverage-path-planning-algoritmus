# main.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
from scipy import ndimage
from calculate_intersection_points import *
# deep_swap, rgb2gray, calculate_edges_coordinates, min_max_coord, degrees_to_slope, plot_parallel_lines, clamp, liang_barsky_clip, bresenham, 
# clip_and_draw_line, edges_of_the_shapes, calculate_distance, connecting_the_points, insert_and_remove_one_coordinate_array, merge_segments, 
# perfect_shapes, find_intersection_of_segments, checking_start_and_end_points1, checking_start_and_end_points2, result_detection,
# edges_of_the_shapes, calculate_intersection_points, find_intersection_of_segments, deleting_bad_intersection_points, 
# selecting_good_lines, trim_line, draw_bresenham_lines, draw_lines

if len(sys.argv) < 2:
    print("Usage: python file_reader_simple.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

try:
    img=mpimg.imread('./Maps/'+filename)
except FileNotFoundError:
    print(f"Error: The '{filename}' the file not found.")

gray_image = rgb2gray(img)

# Define a threshold value
threshold_value = 0.55  # In the range [0, 1] for grayscale images

# Apply the threshold manually
binary_image = np.where(gray_image > threshold_value, 1, 0)
n_binary_image = np.array(binary_image)

labeled_edges, num_features = ndimage.label(n_binary_image)

coordinate_points = calculate_edges_coordinates(labeled_edges, 0)
outside_of_map = calculate_edges_coordinates(labeled_edges, 1)
internal_coordinate_points = calculate_edges_coordinates(labeled_edges, 2)
internal_coordinate_points_of_barrier = calculate_edges_coordinates(labeled_edges, num_features)

n_coordinate_points = np.array(coordinate_points)
n_outside_of_map = np.array(outside_of_map)
n_internal_coordinate_points = np.array(internal_coordinate_points)
n_internal_coordinate_points_of_barrier = np.array(internal_coordinate_points_of_barrier)

min_max_x_y_coord = min_max_coord(coordinate_points)
angle_degrees = 71 # Angle of inclination of the lines
robot_size = 4
scale_factor = 2

lines = draw_parallel_lines_with_angle(img, min_max_x_y_coord, angle_degrees, robot_size, scale_factor)

b_lines = []
for l in lines:
    b_lines.append(bresenham(l[0][0], l[0][1], l[1][0], l[1][1]))

'''for bl in b_lines:
    for b in range(len(bl) - 1):
        #print((bl[b][0], bl[b + 1][0]), (bl[b][1], bl[b + 1][1]))
        plt.plot((bl[b][0], bl[b + 1][0]), (bl[b][1], bl[b + 1][1]), color='red', linewidth=1)
'''
shape_coordinates = []
shape_coordinates.append(connecting_the_points(n_coordinate_points))

insert_and_remove_one_coordinate_array(shape_coordinates)

# Merging when will shape
is_merging = True
is_checking = True
shapes = [] 
while is_merging:
    merge_segments(shape_coordinates[0])
    shape = perfect_shapes(shape_coordinates[0])
    if len(shape) > 0:
        shapes.extend(shape)
    is_merging = checking_start_and_end_points1(shape_coordinates[0])
    if not is_merging:
        while is_checking:
            merge_segments(shape_coordinates[0])
            shape = perfect_shapes(shape_coordinates[0])
            if len(shape) > 0:
                shapes.extend(shape)
            is_checking = checking_start_and_end_points2(shape_coordinates[0])

result_detection(shape_coordinates[0], shapes)

edge_coordinates = edges_of_the_shapes(b_lines, shapes)

intersection_points = calculate_intersection_points(edge_coordinates, b_lines, angle_degrees)

deleting_bad_intersection_points(intersection_points, n_coordinate_points)

finally_b_lines = selecting_good_lines(intersection_points, b_lines, robot_size, n_internal_coordinate_points_of_barrier, n_outside_of_map, n_coordinate_points)

# Cuts off robot-sized distance from bresenhen lines
cut_finally_b_lines = [[] for _ in range(len(finally_b_lines))]
for count, fbl in enumerate(finally_b_lines):
    for bl in fbl:
        cut_finally_b_lines[count].append(trim_line(bl, robot_size))
        
draw_bresenham_lines(cut_finally_b_lines, 'green')

all_segments = [[] for _ in range(len(cut_finally_b_lines))]
for count, cfbl in enumerate(cut_finally_b_lines):
    for bl in cfbl:
        if len(bl) == 0:
            continue
        all_segments[count].append([bl[0], bl[-1]])

for all_s in all_segments:
    print(all_s)


imgplot = plt.imshow(img)
plt.title("Angle= " + str(angle_degrees) + '\nRobot size= ' + str(robot_size))
plt.grid(False)
plt.show()