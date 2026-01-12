import numpy as np
import math

from calculation_of_intersection_points import find_intersection_of_segments
from calculation_of_parallel_lines import bresenham

# staggering_of_main_lines.py

def calculate_intersection_points_with_bresenham(shapes, square_lines, angle_degrees):
    intersection_points = []  

    for square_line in square_lines:
        square_intersections = []  

        for squ_line in square_line:
            all_intersections = set()  

            for s_line in squ_line:
                s_line_intersections = set()  

                for shape in shapes:
                    for s_l in range(len(s_line) - 1):
                        for sh in range(len(shape) - 1):
                            ip = find_intersection_of_segments(
                                shape[sh], shape[sh + 1], 
                                s_line[s_l], s_line[s_l + 1]
                            )

                            if ip is not None:
                                if len(ip) == 2:
                                    r_ip = (
                                        math.floor(ip[0]), math.floor(ip[1])
                                    ) if (0 <= angle_degrees < 90 or 180 <= angle_degrees < 270) else (
                                        math.ceil(ip[0]), math.floor(ip[1])
                                    )
                                    s_line_intersections.add(r_ip)

                                elif len(ip) == 4:
                                    for i in range(0, len(ip), 2):
                                        r_ip = (
                                            math.floor(ip[i]), math.floor(ip[i + 1])
                                        ) if (0 <= angle_degrees < 90 or 180 <= angle_degrees < 270) else (
                                            math.ceil(ip[i]), math.floor(ip[i + 1])
                                        )
                                        s_line_intersections.add(r_ip)

                all_intersections.update(s_line_intersections)

            sorted_intersections = sorted(all_intersections, key=lambda p: (p[0], p[1]))

            square_intersections.append(sorted_intersections if sorted_intersections else [])

        intersection_points.append(square_intersections)

    return intersection_points

def create_boundary_lines_on_the_sections(lines, robot_size):
    robot_size //= 2
    square_lines = [[] for _ in range(len(lines))]  

    for count, line_group in enumerate(lines): 
        for lg in line_group:
            if len(lg) == 0:
                square_lines[count].append([])
            else:
                s_lines = []
                x1, y1 = lg[0]
                x2, y2 = lg[-1]

                # Direction vector calculation
                dx, dy = x2 - x1, y2 - y1

                # Calculating a perpendicular vector (90 degree rotation)
                perp_x, perp_y = dy, -dx
                length = np.sqrt(perp_x**2 + perp_y**2)

                scale = robot_size / length
                dx, dy = perp_x * scale, perp_y * scale

                # Endpoints of a perpendicular line
                x1L, y1L = round(x1 + dx), round(y1 + dy)
                x1R, y1R = round(x1 - dx), round(y1 - dy)
                x2L, y2L = round(x2 + dx), round(y2 + dy)
                x2R, y2R = round(x2 - dx), round(y2 - dy)

                s_lines.extend([
                    [x1L, y1L, x2L, y2L],
                    [x2L, y2L, x2R, y2R],
                    [x2R, y2R, x1R, y1R],
                    [x1R, y1R, x1L, y1L]
                ])

                square_lines[count].append(s_lines) 

    return square_lines

def cut_start_and_end_points_bresenham_lines(b_lines, shapes, robot_size, angle_degrees):
    robot_size //= 2
    cut_lines = []
    for b_line in b_lines:
        if len(b_line) == 0:
            continue

        # Start point
        start_idx = int(robot_size) + 1
        is_ip = True
        while is_ip and len(b_line) > start_idx:
            if start_idx < len(b_line):
                x1, y1 = b_line[start_idx]  
                start_square = []
                xL1, yL1 = round(x1 - robot_size), round(y1 - robot_size)
                xR1, yR1 = round(x1 + robot_size), round(y1 + robot_size)
                start_square.extend([
                    [xL1, yL1, xR1, yL1],  # Top edge
                    [xR1, yL1, xR1, yR1],  # Right edge
                    [xR1, yR1, xL1, yR1],  # Bottom edge
                    [xL1, yR1, xL1, yL1]   # Left edge
                ])
                start_square_b_lines = []
                for ss in start_square:
                        s_s_b_lines = bresenham(ss[0], ss[1], ss[2], ss[3])  # Bresenham lines generation
                        start_square_b_lines.append(s_s_b_lines)
                intersection_points = set()
                for i in range(len(start_square_b_lines)): 
                    s_s_b_lines_1 = start_square_b_lines[i]      # First line set
                    for b_lines in range(0, len(s_s_b_lines_1) - 1):  # Lines within the first set
                        for shape in shapes: 
                            
                            for sh in range(0, len(shape) - 1):  
                                ip = find_intersection_of_segments(
                                    s_s_b_lines_1[b_lines], s_s_b_lines_1[b_lines + 1], 
                                    shape[sh], shape[sh + 1]
                                )
                                if ip is not None:
                                    if len(ip) == 2:  # One piece intersection points
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        intersection_points.add(r_ip)  # Add to set
                                    elif len(ip) == 4:  # Overlapping sections
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        for i in range(0, len(ip) - 1, 2):
                                            intersection_points.add((ip[i], ip[i + 1]))  # Add to set
                if len(intersection_points) > 0:
                    start_idx += 1
                elif len(intersection_points) == 0:
                    is_ip = False
            else:
               start_idx = len(b_line)

        # End point
        end_idx = len(b_line) - int(robot_size) - 1
        is_ip = True
        while is_ip and -(len(b_line)) < end_idx:
            if end_idx < len(b_line):
                x1, y1 = b_line[end_idx]  
                end_square = []
                xL1, yL1 = round(x1 - robot_size), round(y1 - robot_size)
                xR1, yR1 = round(x1 + robot_size), round(y1 + robot_size)
                end_square.extend([
                    [xL1, yL1, xR1, yL1],  # Top edge
                    [xR1, yL1, xR1, yR1],  # Right edge
                    [xR1, yR1, xL1, yR1],  # Bottom edge
                    [xL1, yR1, xL1, yL1]   # Left edge
                ])
                end_square_b_lines = []
                for ss in end_square:
                        s_s_b_lines = bresenham(ss[0], ss[1], ss[2], ss[3])  # Bresenham vonal generálása
                        end_square_b_lines.append(s_s_b_lines)

                intersection_points = set()
                for i in range(len(end_square_b_lines)):  # We go through it in pairs
                    s_s_b_lines_1 = end_square_b_lines[i]     
                    for b_lines in range(0, len(s_s_b_lines_1) - 1):  
                        for shape in shapes:  
                            
                            for sh in range(0, len(shape) - 1):  
                                ip = find_intersection_of_segments(
                                    s_s_b_lines_1[b_lines], s_s_b_lines_1[b_lines + 1], 
                                    shape[sh], shape[sh + 1]
                                )
                                if ip is not None:
                                        
                                    if len(ip) == 2:  # One piece intersection points
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        intersection_points.add(r_ip)  # Add to set
                                    elif len(ip) == 4:  # Overlapping sections
                                        if angle_degrees >= 0 and angle_degrees < 90 or angle_degrees >= 180 and angle_degrees < 270:
                                            r_ip = (math.floor(ip[0]), math.floor(ip[1]))
                                        else:
                                            r_ip = (math.ceil(ip[0]), math.floor(ip[1]))
                                        for i in range(0, len(ip) - 1, 2):
                                            intersection_points.add((ip[i], ip[i + 1]))  # Add to set
                if len(intersection_points) > 0:
                    end_idx -= 1
                elif len(intersection_points) == 0:
                    is_ip = False
            else:
                end_idx = len(b_line)
        # To get to the edge of the map, we subtract 1 from start_idx and add 1 to end_idx
        trimmed_points = b_line[start_idx:end_idx + 1]
        if len(trimmed_points) > 1:
            cut_lines.append(trimmed_points)
    return cut_lines
    
def lines_convert_to_bresenham_lines(square_lines):
    b_s_lines = [[] for _ in range(len(square_lines))]

    for count, s_lines_group in enumerate(square_lines):  
        if not s_lines_group:  
            continue
        
        converted_group = []  
        
        for sl_group in s_lines_group:
            if len(sl_group) == 0:
                continue
            else:
                converted_sl_group = []  
                for slg in sl_group:
                    b_s_l = bresenham(slg[0], slg[1], slg[2], slg[3])  
                    converted_sl_group.append(b_s_l)
                
                converted_group.append(converted_sl_group)
        
        b_s_lines[count] = converted_group  

    return b_s_lines


def cut_bresenham_line_intersection_points(b_lines, intersections, angle_degrees):
    new_lines = []
    for (b_line, ips) in zip(b_lines, intersections):
        if len(b_line) == 0:
            continue  

        if len(ips) > 0:
            if (0 <= angle_degrees < 45) or (135 <= angle_degrees < 225) or (315 <= angle_degrees < 360):
                x = 0  
            elif (45 <= angle_degrees < 135) or (225 <= angle_degrees < 315):
                x = 1  

            sorted_points = sorted(set(p[x] for p in ips))  
            if not sorted_points:
                new_lines.append(b_line)
                continue

            x_or_y_value = set(p[x] for p in b_line)

            # Find the first and last valid intersection points on the line
            min_point = sorted_points[0]
            max_point = sorted_points[-1]

            for v in sorted_points:
                if v in x_or_y_value:
                    min_point = v
                    break 

            for v in reversed(sorted_points):
                if v in x_or_y_value:
                    max_point = v
                    break 

            # Cut a line based on min_point and max_point
            new_line1 = [bl for bl in b_line if bl[x] < min_point]
            new_line2 = [bl for bl in b_line if bl[x] > max_point]

            if len(new_line1) > 1:
                new_lines.append(new_line1)
            if len(new_line2) > 1:
                new_lines.append(new_line2)


        else:
            new_line = [bl for bl in b_line]
            new_lines.append(new_line)

    return new_lines