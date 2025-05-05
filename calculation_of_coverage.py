import numpy as np
import copy
import math
from scipy.ndimage import binary_dilation
from matplotlib.path import Path
import matplotlib.pyplot as plt

from calculation_of_intersection_points import calculate_distance

# calculation_of_coverage.py


def calculating_route_distance(visited_points):
    rout_distance = 0
    for vp in range(len(visited_points) - 1):
        rout_distance += calculate_distance(visited_points[vp], visited_points[vp + 1])
    return rout_distance

# Grid size (based on min-max boundaries, square grid)
def calculate_coverage(shapes, visited_points, robot_size):
    # Define the fixed boundaries of the map (outer_polygon)
    outer_polygon = shapes[0]  # Map
    xmin, ymin = outer_polygon.min(axis=0)
    xmax, ymax = outer_polygon.max(axis=0)

    # Fix the size of the grid based on the map so that it does not change according to the route
    grid_size = (ymax - ymin + 1, xmax - xmin + 1)  # Width, Height

    # Initialisation of the grid
    original_grid = np.zeros(grid_size, dtype=np.uint8)

    # Initialising the paths of external and internal polygons
    outer_path = Path(outer_polygon)
    inner_paths = [Path(inner) for inner in shapes[1:]]

    for y in range(grid_size[0]):
        for x in range(grid_size[1]):
            real_x, real_y = x + xmin, y + ymin
            point = (real_x, real_y)

            if not outer_path.contains_point(point, radius=-1e-9):
                original_grid[y, x] = 0
            else:
                is_inner = any(inner.contains_point(point, radius=-1e-9) for inner in inner_paths)
                is_on_shape_edge = any(
                    any(
                        math.isclose(segment_point[0], point[0], abs_tol=0.5) and 
                        math.isclose(segment_point[1], point[1], abs_tol=0.5)
                        for segment_point in shape
                    ) for shape in shapes
                )

                if is_inner or is_on_shape_edge:
                    original_grid[y, x] = 0
                else:
                    original_grid[y, x] = 1

    grid = original_grid.copy()

    # Tracking the robot's path
    for i in range(len(visited_points) - 1):
        x1, y1 = visited_points[i]
        x2, y2 = visited_points[i + 1]

        num_steps = max(abs(x2 - x1), abs(y2 - y1))
        for step in range(num_steps + 1):
            real_x, real_y = (x1, y1) if num_steps == 0 else (
                int(round(x1 + step * (x2 - x1) / num_steps)),
                int(round(y1 + step * (y2 - y1) / num_steps))
            )

            x_grid, y_grid = real_x - xmin, real_y - ymin

            if 0 <= x_grid < grid_size[1] and 0 <= y_grid < grid_size[0]:
                if grid[y_grid, x_grid] == 1:  # Only on valid cells
                    grid[y_grid, x_grid] = 2  # Plot the robot's route

    # Robot size taking into account dilatation
    structure = np.ones((robot_size, robot_size))  
    dilated_grid = binary_dilation(grid == 2, structure=structure)

    # Calculating the area covered
    covered_area = np.sum(dilated_grid & (grid == 1)) + np.sum(grid == 2)
    total_area = np.sum(original_grid == 1)  
    coverage_percentage = (covered_area / total_area) * 100

    
    # Graphical display
    plt.figure(figsize=(6, 6))
    plt.imshow(grid, cmap="gray_r", origin="upper")
    plt.imshow(dilated_grid, cmap="Blues", alpha=0.6, origin="upper")

    plt.plot([p[0] - xmin for p in visited_points], 
            [p[1] - ymin for p in visited_points], 
            'r-', linewidth=1.5)

    plt.scatter(outer_polygon[:, 0] - xmin, outer_polygon[:, 1] - ymin, color="black")

    for inner in shapes[1:]:
        plt.scatter(inner[:, 0] - xmin, inner[:, 1] - ymin, color="blue")

    plt.title("Area covered by robot")

    result_text = f"Result\nCovered area: {covered_area} cells\nTotal area:       {total_area} cells\nCoverage:       {coverage_percentage:.2f}%"

    plt.subplots_adjust(bottom=0.1) 
    plt.figtext(0.005, 0.005, result_text, ha='left', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))
    plt.show()
