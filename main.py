import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
import sys
from scipy import ndimage
from animation import animation_of_result
from graph import *
# creating_nearborn_list, connecting_sections, heapify_up, heapify_down, push_heap, pop_heap, dijkstra
from area import calculating_route_distance, create_grid
from calculate_intersection_points import *
# deep_swap, rgb2gray, calculate_edges_coordinates, min_max_coord, degrees_to_slope, plot_parallel_lines, clamp, liang_barsky_clip, bresenham, 
# clip_and_draw_line, edges_of_the_shapes, calculate_distance, connecting_the_points, insert_and_remove_one_coordinate_array, merge_segments, 
# perfect_shapes, find_intersection_of_segments, checking_start_and_end_points1, checking_start_and_end_points2, result_detection,
# edges_of_the_shapes, calculate_intersection_points, find_intersection_of_segments, deleting_bad_intersection_points, 
# selecting_good_lines, trim_line, draw_bresenham_lines, draw_lines
import time


start_time = time.perf_counter()

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

angle_degrees = 0 # Angle of inclination of the lines
robot_size = 7
scale_factor = 2

lines = draw_parallel_lines_with_angle(img, min_max_x_y_coord, angle_degrees, robot_size, scale_factor)

b_lines = []
for l in lines:
    b_lines.append(bresenham(l[0][0], l[0][1], l[1][0], l[1][1]))

shape_coordinates = []
shape_coordinates.append(connecting_the_points(n_coordinate_points))

insert_and_remove_one_coordinate_array(shape_coordinates)

# Merging when will shape
is_merging = True
is_checking = True
polygon = [] 
while is_merging:
    merge_segments(shape_coordinates[0])
    shape = perfect_shapes(shape_coordinates[0])
    if len(shape) > 0:
        polygon.extend(shape)
    is_merging = checking_start_and_end_points1(shape_coordinates[0])
    if not is_merging:
        while is_checking:
            merge_segments(shape_coordinates[0])
            shape = perfect_shapes(shape_coordinates[0])
            if len(shape) > 0:
                polygon.extend(shape)
            is_checking = checking_start_and_end_points2(shape_coordinates[0])

the_biggest_polygon = max(polygon, key=len)

shapes = [the_biggest_polygon] + [shape for shape in polygon if shape is not the_biggest_polygon]

result_detection(shape_coordinates[0], shapes)

edge_coordinates = edges_of_the_shapes(b_lines, shapes)

intersection_points = calculate_intersection_points(edge_coordinates, b_lines, angle_degrees)

deleting_bad_intersection_points(intersection_points, n_coordinate_points)

good_b_lines = selecting_good_lines(intersection_points, b_lines, robot_size, n_internal_coordinate_points_of_barrier, n_outside_of_map, n_coordinate_points)

cut_good_b_lines = []
for g_b_lines in good_b_lines:
    if len(g_b_lines) == 0:
        continue
    c_g_b_line = cut_start_and_end_points_bresenham_lines(g_b_lines, shapes, robot_size, angle_degrees)
    if c_g_b_line:
        cut_good_b_lines.append(c_g_b_line)
            
square_lines_on_the_sections = create_boundary_lines_on_the_sections(cut_good_b_lines, robot_size)

b_s_lines_on_the_sections = lines_convert_to_bresenham_lines(square_lines_on_the_sections)

intersection_points_on_the_sections = calculate_intersection_points_with_bresenham(shapes, b_s_lines_on_the_sections, robot_size)

cut_sections = []
for  cgbl, ips in zip(cut_good_b_lines, intersection_points_on_the_sections):
    if len(cgbl) == 0:
        continue
    cut_section =  cut_bresenham_line_intersection_points(cgbl, ips, angle_degrees)
    cut_sections.append(cut_section)

good_cut_sections = [[] for _ in range(len(cut_sections))]
for count, c_sections in enumerate(cut_sections):
    for cs in c_sections:
        good_cut_sections[count].append([cs[0], cs[-1]])  # Első és utolsó elem hozzáadása

# Merges internal lists
finally_good_cut_sections = [sum(gcs, []) for gcs in good_cut_sections if gcs]

#Creating_nearborn_list
neighborhood_list = creating_nearborn_list(finally_good_cut_sections, shapes)

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

two_path_equil = False
actual_path = []
while len(visited_points_set) != len(neighborhood_list) and not(two_path_equil):
    dict_keys = list(neighborhood_list.keys())
    missing_in_list = [key for key in dict_keys if key not in visited_points]

    previous_path = actual_path
    distances = {}
    for ml in missing_in_list:
        distance, path = dijkstra(neighborhood_list, visited_points[-1], ml)
        distances[distance] = path

    min_distance = min(distances.keys())
    actual_path = distances[min_distance]

    if actual_path == previous_path:
        visited_points = visited_points[:-len(previous_path)] if len(visited_points) >= len(previous_path) else []
        print('No further connection between sections')
        two_path_equil = True
    else:
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
ani = animation_of_result(all_points, ax, robot_size)

# Tittle setting
ax.set_title("ISOC")

ax.grid(False)

time.sleep(2)

end_time = time.perf_counter()
elapsed_time = end_time - start_time

result_text = f"Angle: {angle_degrees}             Robot size: {robot_size}\nRoute distance: {route_distance:.2f}\nRunning time:    {elapsed_time:.6f} seconds"

plt.subplots_adjust(bottom=0.1) 

plt.figtext(0.25, 0.1, result_text, ha='center', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

# Save in the gif
#ani.save("my_room.gif", writer="pillow", fps=60)

plt.show()

create_grid(shapes, visited_points, robot_size)