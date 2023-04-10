from matplotlib import image
from matplotlib import pyplot as plt
import numpy as np
import math


def sortFirst(val):
    return val[0]

def ones(a):
    if a.size == 0:
        return True
    else:
        for i in a:
            if i == 0:
                return False
    return True

def index_of_array(bp, val):
    idx_list = []
    bp = np.array(black_points) 
    bp[:, [1, 0]] = bp[:, [0, 1]]
    idx = np.where(bp == val)
    if ones(idx[1]):
        idx_list.append(False)
        return idx_list
    else:
        idx_list.append(True)
        l = []
        for i in range(len(idx[1])):
            if idx[1][i] == 0:
                l.append(idx[0][i])
        idx_list.append(l)
        return idx_list
 
def save_line(x1, x2, y1, y2_last):
    line = []
    y2 = []
    for i in range(1, y2_last):
        y2.append(i)
    line.append(x1)
    line.append(x2)
    line.append(y1)
    line.append(y2)
    return line

def draw_lines(lines, c):
    for ln in lines:
        plt.plot((ln[0], ln[1]), (ln[2], ln[3][-1]), color=c, linewidth=1)
        
def two_points_between_distance(green_lines):
    distance = 0.0
    d = 0.0
    for gl in green_lines:
        d = math.sqrt(((gl[1] - gl[0])**2) + ((gl[3][-1] - gl[2])**2))
        distance += d
        d = 0.0
    return distance

data = image.imread('Map5.png')

#search black points in image

cnt = 0
coord = [] 
black_points = [] 
black = False
for y in range(5, data.shape[1] - 5):
    black = False
    for x in range(5, data.shape[0] - 5):
        for k in range(data.shape[2]):
            if data[x, y, k] == 0:
                cnt += 1
                black = True
                coord += x, y
                black_points.append(coord)
                coord = []
                break
        
        if black:
            break

for y in range(data.shape[1] - 5, 5, -1):
    black = False
    for x in range(data.shape[0] - 5, 5, -1):
        for k in range(data.shape[2]):
            if data[x, y, k] == 0:
                cnt += 1
                black = True
                coord += x, y
                black_points.append(coord)
                coord = []
                break
        
        if black:
            break

#save in array lines
lines = []
x1 = 5
x2 = 5
y1 = 5
y2 = data.shape[0]
while x1 < data.shape[1] and x2 < data.shape[1]:
    lines.append(save_line(x1, x2, y1, y2))
    x1 += 10
    x2 += 10
 
# draw lines
draw_lines(lines, "blue")


#intersection points
intersection_points = []
l = []
line_points = []
np.asarray(black_points)
for x, y, z1, z2 in lines:
    for i in z2:
        l.append(i)
        l.append(x)
        line_points.append(l)
        l = []
np.asarray(line_points)
for x in black_points:
    for y in line_points:
        if x == y:
            intersection_points.append(x)

for x in intersection_points:
    plt.scatter(x[1], x[0], color='red')

#sort array first value
black_points.sort(key=sortFirst)
bp = np.array(black_points)

#road
green_lines = []
for ln in lines:
    idx_list = index_of_array(bp, ln[0])
    if idx_list[0] == False:
        green_lines.append(save_line(ln[0], ln[1], ln[2], ln[3][-1]))
    else:
        green_lines.append(save_line(ln[0], ln[1], ln[2], black_points[idx_list[1][0]][0]))
        green_lines.append(save_line(ln[0],  ln[1], black_points[idx_list[1][1]][0],ln[3][-1]))
        
draw_lines(green_lines, "green")
distance = two_points_between_distance(green_lines)
print("Tavolsag: ", distance)
plt.imshow(data)
plt.show()