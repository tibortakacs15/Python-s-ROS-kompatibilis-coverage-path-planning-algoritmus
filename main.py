
# main.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
from scipy import ndimage
from calculate_intersection_points import *
#rgb2gray, calculate_edges_coordinates, min_max_coord, degrees_to_slope, plot_parallel_lines, edges_of_the_shapes, calculate_distance, connecting_the_points, insert_and_remove_one_coordinate_array, merge_segments, find_intersection_of_segments, calculate_intersection_points, cut_line_segment

# Draw lines in map
def draw_lines(points, color):
    for pt in points:
        if pt == []:
            continue
        else:
            for p in range(0,len(pt) - 1, 2):
                plt.plot((pt[p][0], pt[p + 1][0]), (pt[p][1], pt[p + 1][1]), color=color, linewidth=1)

if len(sys.argv) < 2:
    print("Használat: python file_olvaso_simple.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

try:
    img=mpimg.imread('./Maps/'+filename)
except FileNotFoundError:
    print(f"Error: A '{filename}' the file not found.")

gray_image = rgb2gray(img)

# Define a threshold value
threshold_value = 0.55  # In the range [0, 1] for grayscale images

# Apply the threshold manually
binary_image = np.where(gray_image > threshold_value, 1, 0)
n_binary_image = np.array(binary_image)

labeled_edges, num_features = ndimage.label(n_binary_image)

coordinate_points = calculate_edges_coordinates(labeled_edges, 0)
internal_coordinate_points = calculate_edges_coordinates(labeled_edges, 2)
internal_coordinate_points_of_barrier = calculate_edges_coordinates(labeled_edges, num_features)


n_coordinate_points = np.array(coordinate_points)
n_internal_coordinate_points = np.array(internal_coordinate_points)
n_internal_coordinate_points_of_barrier = np.array(internal_coordinate_points)

min_max_x_y_coord = min_max_coord(coordinate_points)

angle_degrees = 0 # Angle of inclination of the lines
robot_size = 17
scale_factor = 1.4

lines = draw_parallel_lines_with_angle(img, angle_degrees, robot_size, scale_factor, min_max_x_y_coord)

shape_coordinates = []
shape_coordinates.append(connecting_the_points(n_coordinate_points))

insert_and_remove_one_coordinate_array(shape_coordinates)

merge_segments(shape_coordinates[0])

intersection_points = calculate_intersection_points(shape_coordinates[0], n_coordinate_points, n_internal_coordinate_points_of_barrier, lines, angle_degrees)

# Cutting segments from the start and end points of the robot size
new_intersection_points = [[] for _ in range(len(intersection_points))]
for ip in range(len(intersection_points)):
    for i in range(0,len(intersection_points[ip]) - 1, 2): 
        if cut_line_segment(intersection_points[ip][i][0], intersection_points[ip][i][1], intersection_points[ip][i + 1][0], intersection_points[ip][i + 1][1], robot_size // 2):
            new_intersection_points[ip].append(cut_line_segment(intersection_points[ip][i][0], intersection_points[ip][i][1], intersection_points[ip][i + 1][0], intersection_points[ip][i + 1][1], robot_size // 2))

# Draw segments
for nip in new_intersection_points:
    for n in range(len(nip)):
        plt.plot((nip[n][0], nip[n][2]), (nip[n][1], nip[n][3]), color='blue')

imgplot = plt.imshow(img)
plt.grid(False)
plt.show()