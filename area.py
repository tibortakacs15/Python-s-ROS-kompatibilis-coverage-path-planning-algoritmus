import numpy as np
from scipy.ndimage import binary_dilation
from matplotlib.path import Path
import matplotlib.pyplot as plt
from calculate_intersection_points import calculate_distance

# arrea.py

def calculating_route_distance(visited_points):
    rout_distance = 0
    for vp in range(len(visited_points) - 1):
        rout_distance += calculate_distance(visited_points[vp], visited_points[vp + 1])
    return rout_distance

# Raster mérete (min-max határok alapján, négyzetrács)
def create_grid(shapes, visited_points, robot_size):
    outer_polygon = shapes[0]  # Map
    inner_polygons = shapes[1:]  # Barriers

    xmin, ymin = outer_polygon.min(axis=0)
    xmax, ymax = outer_polygon.max(axis=0)
    grid_size = (ymax - ymin + 1, xmax - xmin + 1)  # Width, heigth

    # Create a drid
    grid = np.zeros(grid_size, dtype=np.uint8)

    # Convert map and obstacles into route objects
    outer_path = Path(outer_polygon)
    inner_paths = [Path(inner) for inner in inner_polygons]

    # Finding valid cells within a map
    for y in range(grid_size[0]):
        for x in range(grid_size[1]):
            real_x, real_y = x + xmin, y + ymin 

            if outer_path.contains_point((real_x, real_y)):  
                if not any(inner_path.contains_point((real_x, real_y)) for inner_path in inner_paths):  
                    grid[y, x] = 1  # Valid area

    # Placing a robot's path on a grid
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
                if grid[y_grid, x_grid] == 1:  #Only if the shape is in valid area
                    grid[y_grid, x_grid] = 2  

    # Robot size
    structure = np.ones((robot_size, robot_size))  
    dilated_grid = binary_dilation(grid == 2, structure=structure)

    # Calculation of covered area
    covered_area = np.sum(dilated_grid & (grid == 1))
    total_area = np.sum(grid == 1)  
    coverage_percentage = (covered_area / total_area) * 100

    print(f"Covered area: {covered_area} cell")
    print(f"Total area: {total_area} cell")
    print(f"Coverage percentage: {coverage_percentage:.2f}%")

 
    plt.figure(figsize=(6, 6))
    plt.imshow(grid, cmap="gray_r", origin="upper")
    plt.imshow(dilated_grid, cmap="Blues", alpha=0.6, origin="upper")

    plt.plot([p[0] - xmin for p in visited_points], 
             [p[1] - ymin for p in visited_points], 
             'r-', linewidth=1.5)
    
    plt.scatter(outer_polygon[:, 0] - xmin, outer_polygon[:, 1] - ymin, color="black")
    
    for inner in inner_polygons:
        plt.scatter(inner[:, 0] - xmin, inner[:, 1] - ymin, color="blue")

    plt.legend()
    plt.title("Area covered by robot")
    
    result_text = f"Result\nCovered area: {covered_area} cells\nTotal area:       {total_area} cells\nCoverage:       {coverage_percentage:.2f}%"

    plt.subplots_adjust(bottom=0.1) 

    plt.figtext(0.15, 0.1, result_text, ha='left', fontsize=12, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))
    
    plt.show()