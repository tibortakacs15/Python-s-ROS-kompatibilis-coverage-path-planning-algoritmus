from matplotlib import image
from matplotlib import pyplot as plt
import numpy as np
import math
import time


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
 
def save_line1(x1, x2, y1, y2_last):
    line = []
    y2 = []
    for i in range(1, y2_last):
        y2.append(i)
    line.append(x1)
    line.append(x2)
    line.append(y1)
    line.append(y2)
    return line

def save_line2(x1, y1, y2):
    line = []
    line.append(x1)
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

#Map reading
start_time = time.time()
data = image.imread('Map5.png')
mr = 31
half_of_mr = mr // 2

#search black points in image
coord = [] 
black_points = [] 
black = False
for y in range(half_of_mr, data.shape[1] - half_of_mr, half_of_mr):
    black = False
    for x in range(half_of_mr, data.shape[0] - half_of_mr):
        for k in range(data.shape[2]):
            if data[x, y, k] == 0:
                black = True
                coord += x, y
                black_points.append(coord)
                coord = []
                break
        
        if black:
            break
end = y
for y in range(end, 0, -half_of_mr):
    black = False
    for x in range(data.shape[0] - half_of_mr, half_of_mr, -1):
        for k in range(data.shape[2]):
            if data[x, y, k] == 0:
                black = True
                coord += x, y
                black_points.append(coord)
                coord = []
                break
        
        if black:
            break

#save in array lines
lines = []
x1 = half_of_mr
x2 = half_of_mr
y1 = half_of_mr
y2 = data.shape[0] - half_of_mr
while x1 < data.shape[1] and x2 < data.shape[1]:
    lines.append(save_line1(x1, x2, y1, y2))
    x1 += half_of_mr
    x2 += half_of_mr
 
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
all_lines = []
full_lines = []
half_lines1 = []
half_lines2 = []
for ln in lines:
    idx_list = index_of_array(bp, ln[0])
    if idx_list[0] == False:
        if len(half_lines1) > 0 and len(half_lines2) > 0:
            all_lines.append(half_lines1)
            all_lines.append(half_lines2)
            half_lines1 = []
            half_lines2 = []
        green_lines.append(save_line1(ln[0], ln[1], ln[2], ln[3][-1]))
        auxiliary_list1 = save_line2(ln[0], ln[2], ln[3][-1])
        full_lines.append(auxiliary_list1)
    else:
        if len(full_lines) > 0:
            all_lines.append(full_lines)
            full_lines = []
        green_lines.append(save_line1(ln[0], ln[1], ln[2], black_points[idx_list[1][0]][0]))
        auxiliary_list2 = save_line2(ln[0], ln[2], black_points[idx_list[1][0]][0])
        half_lines1.append(auxiliary_list2)
        green_lines.append(save_line1(ln[0],  ln[1], black_points[idx_list[1][1]][0],ln[3][-1]))
        auxiliary_list3 = save_line2(ln[1], black_points[idx_list[1][1]][0],ln[3][-1])
        half_lines2.append(auxiliary_list3)
all_lines.append(full_lines)

#distances     
draw_lines(green_lines, "green")
distance = two_points_between_distance(green_lines)
print("Tavolsag: ", distance)

#running time
end_time = time.time()
print("--- %s seconds ---" % ( end_time- start_time))

plt.imshow(data)
plt.show()

