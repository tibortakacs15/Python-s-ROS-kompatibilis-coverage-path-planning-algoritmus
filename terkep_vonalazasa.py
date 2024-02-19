import cv2
import numpy as np
from matplotlib import image
from matplotlib import pyplot as plt

# min and max x,y coordinate
def min_max_coord(coordinate_points):
    x_coord = []
    y_coord = []
    for pt in coordinate_points:
        for p in range(len(pt)):
            x_coord.append(pt[0,0])
            y_coord.append(pt[0,1])
    min_x_coord = min(x_coord)
    max_x_coord = max(x_coord)
    min_y_coord = min(y_coord)
    max_y_coord = max(y_coord)
    return min_x_coord, max_x_coord, min_y_coord, max_y_coord


# Filter contours
def lines(coordinate_points, robot_size):
    lst = []
    lines_coordinate_points = []
    for pt in coordinate_points:
        lst.append(pt[0])
    points = np.array(lst)
    for y_coord in range(min_y_coord + robot_size, max_y_coord - robot_size, robot_size):
        idx = np.where((points == y_coord))[0]
        y_coord_withaut_filter = [points[y] for y in idx if points[y][1] == y_coord]
        sort_y_coord_withaut_filter = sorted(y_coord_withaut_filter,key=lambda x: (x[0]))
        delete_points = [y + 1 for y in range(len(sort_y_coord_withaut_filter) -1) if  sort_y_coord_withaut_filter[y + 1][0] - sort_y_coord_withaut_filter[y][0] == 1]
        sort_y_coord_after_filter = np.delete(sort_y_coord_withaut_filter, delete_points, 0)
        lines_coordinate_points.append(sort_y_coord_after_filter)
        idx = []
    return lines_coordinate_points

pictures_map = './Maps/Map0.png'

# read image
img = cv2.imread(pictures_map)

# convert to grayscale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# threshold and invert so hexagon is white on black background
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
thresh = 255 - thresh

# get contours
result = np.zeros_like(img)
contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
contours = contours[0] if len(contours) == 2 else contours[1]
coordinate_points = contours[0]
cv2.drawContours(result, [coordinate_points], 0, (255,255,255), 1)

# to read the image stored in the working directory
data = image.imread(pictures_map)

# Draw shape corners
min_x_coord, max_x_coord, min_y_coord, max_y_coord = min_max_coord(coordinate_points)
plt.scatter(min_x_coord, min_y_coord, color='red')
plt.scatter(min_x_coord, max_y_coord, color='blue')
plt.scatter(max_x_coord, max_y_coord, color='yellow')
plt.scatter(max_x_coord, min_y_coord,  color='green')


# Draw lines
    
robot_size = 10
lines_coordinate_points  = lines(coordinate_points, robot_size)
for lcp in lines_coordinate_points:
    for y in range(0, len(lcp) - 1, 2):
        plt.plot((lcp[y][0], lcp[y + 1][0]), (lcp[y][1], lcp[y + 1][1]), color="blue", linewidth=1)
plt.imshow(data)
plt.grid()
plt.show()
