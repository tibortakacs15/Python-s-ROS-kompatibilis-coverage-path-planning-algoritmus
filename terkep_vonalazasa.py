import cv2
import numpy as np
from matplotlib import image
from matplotlib import pyplot as plt

# min and max x,y coordinate
def min_max_coord(terkep_szele):
    x_coord = []
    y_coord = []
    for pt in terkep_szele:
        x_coord.append(pt[0])
        y_coord.append(pt[1])
    min_x_coord = min(x_coord)
    max_x_coord = max(x_coord)
    min_y_coord = min(y_coord)
    max_y_coord = max(y_coord)
    return min_x_coord, max_x_coord, min_y_coord, max_y_coord

# Filter contours
def filter_contours(contours):
    terkep_szele = []
    akadaly_szele = []
    for i in range(0, len(contours), 2):
        if i == 0:
            for ct in contours[i]:
                terkep_szele.append(ct[0])
        else:
            for ct in contours[i]:
                akadaly_szele.append(ct[0])
    return terkep_szele, akadaly_szele
    

# Lines vertical

def lines_horizontal(coordinate_points, robot_size):
    lines_coordinate_points = []
    points = np.array(coordinate_points)
    for y_coord in range(min_y_coord + robot_size, max_y_coord, robot_size):
        idx = np.where((points == y_coord))[0]
        y_coord_withaut_filter = [points[y] for y in idx if points[y][1] == y_coord]
        sort_y_coord_withaut_filter = sorted(y_coord_withaut_filter,key=lambda x: (x[0]))
        delete_points = [y + 1 for y in range(len(sort_y_coord_withaut_filter) -1) if  (sort_y_coord_withaut_filter[y + 1][0] - sort_y_coord_withaut_filter[y][0] == 1) or (sort_y_coord_withaut_filter[y][0] == sort_y_coord_withaut_filter[y + 1][0])]
        sort_y_coord_after_filter = np.delete(sort_y_coord_withaut_filter, delete_points, 0)
        if len(sort_y_coord_after_filter) > 0:
            lines_coordinate_points.append(sort_y_coord_after_filter)
        else: lines_coordinate_points.append([[0]])
        idx = []
    return lines_coordinate_points

# Lines horizontal
def lines_vertical(coordinate_points, robot_size):
    lines_coordinate_points = []
    points = np.array(coordinate_points)
    for x_coord in range(min_x_coord + robot_size, max_x_coord, robot_size):
        idx = np.where((points == x_coord))[0] 
        x_coord_withaut_filter = [points[x] for x in idx if points[x][0] == x_coord]
        sort_x_coord_withaut_filter = sorted(x_coord_withaut_filter,key=lambda xx: (xx[1]))
        delete_points = [x + 1 for x in range(len(sort_x_coord_withaut_filter) -1) if  (sort_x_coord_withaut_filter[x + 1][1] - sort_x_coord_withaut_filter[x][1] == 1) or (sort_x_coord_withaut_filter[x][1] == sort_x_coord_withaut_filter[x + 1][1])]
        sort_x_coord_after_filter = np.delete(sort_x_coord_withaut_filter, delete_points, 0)
        if len(sort_x_coord_after_filter) > 0:
            lines_coordinate_points.append(sort_x_coord_after_filter)
        else: lines_coordinate_points.append([[0]])
        idx = [] 
    return lines_coordinate_points


# Draw lines
def draw_lines_horizontal(lines_coordinate_points_in_map, lines_coordinate_points_in_shape):
    for lcpm, lcps in zip(lines_coordinate_points_in_map, lines_coordinate_points_in_shape):
        if lcps[0][0] == 0:
            for x in range(0, len(lcpm) - 1, 2):
                plt.plot((lcpm[x][0] + robot_size, lcpm[x + 1][0] - robot_size), (lcpm[x][1], lcpm[x + 1][1]), color="red", linewidth=1)
                plt.scatter(lcpm[x][0] + robot_size, lcpm[x][1],  color='green')
                plt.scatter(lcpm[x + 1][0] - robot_size, lcpm[x + 1][1],  color='green')
        else:
            arr = []
            for pt in range(len(lcpm)):
                arr.append(lcpm[pt][0])
            for pt in range(len(lcps)):
                arr.append(lcps[pt][0])
            sort_arr = sorted(arr)
            y = lcps[pt][1]
            for x in range(0, len(sort_arr) - 1, 2):
                plt.plot((sort_arr[x] + robot_size, sort_arr[x + 1] - robot_size), (y, y), color="red", linewidth=1)
                plt.scatter(sort_arr[x] + robot_size, y,  color='green')
                plt.scatter(sort_arr[x + 1] - robot_size, y, color='green')
            arr = []

def draw_lines_vertical(lines_coordinate_points_in_map, lines_coordinate_points_in_shape):
    for lcpm, lcps in zip(lines_coordinate_points_in_map, lines_coordinate_points_in_shape):
        if lcps[0][0] == 0:
            for x in range(0, len(lcpm) - 1, 2):
                plt.plot((lcpm[x][0], lcpm[x + 1][0]), (lcpm[x][1] + robot_size, lcpm[x + 1][1] - robot_size), color="red", linewidth=1)
                plt.scatter(lcpm[x][0], lcpm[x][1] + robot_size,  color='green')
                plt.scatter(lcpm[x + 1][0], lcpm[x + 1][1] - robot_size,  color='green')
        else:
            arr = []
            for pt in range(len(lcpm)):
                arr.append(lcpm[pt][1])
            for pt in range(len(lcps)):
                arr.append(lcps[pt][1])
            sort_arr = sorted(arr)
            x = lcps[pt][0]
            for y in range(0, len(sort_arr) - 1, 2):
                plt.plot((x, x), (sort_arr[y] + robot_size, sort_arr[y + 1] - robot_size), color="red", linewidth=1)
                plt.scatter(x , sort_arr[y] + robot_size,  color='green')
                plt.scatter(x, sort_arr[y + 1] - robot_size, color='green')
            arr = []


pictures_map = './Maps/Map3_with_barrier.png'

# read image
img = cv2.imread(pictures_map)

# convert to grayscale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# threshold and invert so hexagon is white on black background
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
thresh = 255 - thresh

# get contours
contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
contours = contours[0] if len(contours) == 2 else contours[1]

# to read the image stored in the working directory
data = image.imread(pictures_map)


robot_size = 11
terkep_szele, akadaly_szele = filter_contours(contours)
min_x_coord, max_x_coord, min_y_coord, max_y_coord = min_max_coord(terkep_szele)

plt.scatter(min_x_coord, min_y_coord, color='red')
plt.scatter(min_x_coord, max_y_coord, color='blue')
plt.scatter(max_x_coord, max_y_coord, color='yellow')
plt.scatter(max_x_coord, min_y_coord,  color='green')

lines_coordinate_points_in_map  = lines_vertical(terkep_szele, robot_size)
lines_coordinate_points_in_shape  = lines_vertical(akadaly_szele, robot_size)

# Draw lines
draw_lines_vertical(lines_coordinate_points_in_map, lines_coordinate_points_in_shape)

plt.imshow(data)
plt.grid()
plt.show()
