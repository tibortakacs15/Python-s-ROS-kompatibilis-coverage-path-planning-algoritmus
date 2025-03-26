# main.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
import sys
from scipy import ndimage
from animation import animation_of_result
from graph import *
# creating_nearborn_list, connecting_sections, heapify_up, heapify_down, push_heap, pop_heap, dijkstra
from area import calculating_route_distance
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

fig, ax = plt.subplots()

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
angle_degrees = 358 # Angle of inclination of the lines
robot_size = 14
scale_factor = 2

lines = draw_parallel_lines_with_angle(img, min_max_x_y_coord, angle_degrees, robot_size, scale_factor)

b_lines = []
for l in lines:
    b_lines.append(bresenham(l[0][0], l[0][1], l[1][0], l[1][1]))

'''for bl in b_lines:
    for b in range(len(bl) - 1):
        #print((bl[b][0], bl[b + 1][0]), (bl[b][1], bl[b + 1][1]))
        plt.plot((bl[b][0], bl[b + 1][0]), (bl[b][1], bl[b + 1][1]), color='red', linewidth=1)'''

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

#draw_bresenham_lines(finally_b_lines, 'blue')

# Cuts off robot-sized distance from bresenhen lines
cut_finally_b_lines = [[] for _ in range(len(finally_b_lines))]
for count, fbl in enumerate(finally_b_lines):
    for bl in fbl:
        cut_finally_b_lines[count].append(trim_line(bl, robot_size))

#draw_bresenham_lines(cut_finally_b_lines, 'green')

all_segments = [[] for _ in range(len(cut_finally_b_lines))]
for count, cfbl in enumerate(cut_finally_b_lines):
    for bl in cfbl:
        if len(bl) == 0:
            continue
        all_segments[count].append([bl[0], bl[-1]])

alls_segments = [sum(sublist, []) for sublist in all_segments if sublist]

#Creating_nearborn_list
neighborhood_list = creating_nearborn_list(alls_segments, shapes)

first_point = next(iter(neighborhood_list))
second_point = neighborhood_list[first_point][0][0]

if second_point in neighborhood_list and neighborhood_list[second_point]:
    closest_point = min(neighborhood_list[second_point], key=lambda x: x[1])  # Select the smallest distance
    second_point = neighborhood_list[closest_point[0]][0][0]

# Create a section
first_point = next(iter(neighborhood_list))
second_point = neighborhood_list[first_point][0][0]

visited_points = []
visited_points = connecting_sections(neighborhood_list, first_point, second_point, visited_points)

visited_points_set = set(visited_points)

while len(visited_points_set) != len(neighborhood_list):
    dict_keys = list(neighborhood_list.keys())
    missing_in_list = [key for key in dict_keys if key not in visited_points]

    distances = {}
    for ml in missing_in_list:
        distance, path = dijkstra(neighborhood_list, visited_points[-1], ml)
        distances[distance] = path

    min_distance = min(distances.keys())
    for md in range(1, len(distances[min_distance])):
        visited_points.append(distances[min_distance][md])

    point = visited_points[-1]
    if point in neighborhood_list:
        pozicio = list(neighborhood_list.keys()).index(point)
    else:
        print("There is no such point the neighborhood list.")
    
    first_point = list(neighborhood_list.keys())[pozicio]
    second_point = neighborhood_list[first_point][0][0]

    visited_points = connecting_sections(neighborhood_list, first_point, second_point, visited_points)

    visited_points_set = set(visited_points)
    print(len(neighborhood_list), len(visited_points_set)) # Checking that we have covered all points

#print(visited_points)

for vp in range(len(visited_points) - 1):
    ax.plot((visited_points[vp][0], visited_points[vp + 1][0]), (visited_points[vp][1], visited_points[vp + 1][1]), color='red')

ax.scatter(visited_points[0][0], visited_points[0][1], color='blue')
ax.scatter(visited_points[-1][0], visited_points[-1][1], color='gray')

all_points = []
for p in range(len(visited_points) - 1):
    all_points.append(bresenham(visited_points[p][0], visited_points[p][1], visited_points[p + 1][0], visited_points[p + 1][1]))

# Calculating route distance
route_distance = calculating_route_distance(visited_points)

#Show result on image
imgplot = ax.imshow(img)  

# Animation initialization
ani = animation_of_result(all_points, ax)

# Tittle setting
ax.set_title(f"Angle= {angle_degrees}\nRobot size= {robot_size}\nRoute distance= {route_distance}")

ax.grid(False)

# Save in the gif
#ani.save("my_room.gif", writer="pillow", fps=30)

plt.show()
