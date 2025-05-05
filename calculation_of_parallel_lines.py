import numpy as np
import math

# calculation_of_parallel_lines.py

def draw_parallel_lines_with_angle(image, min_max_x_y_coord, angle_degrees, robot_size, scale_factor):
    height, width = image.shape[:2]
    spacing = robot_size

    # Angle degree to radian
    angle_radians = math.radians(angle_degrees)
    
    # Special cases for 0°, 90°, 180°, 270°
    if angle_degrees == 0:
        offset_x, offset_y = 0, spacing
    elif angle_degrees == 90:
        offset_x, offset_y = spacing, 0
    elif angle_degrees == 180:
        offset_x, offset_y = 0, -spacing
    elif angle_degrees == 270:
        offset_x, offset_y = -spacing, 0
    else:
        offset_x = spacing * math.sin(angle_radians)
        offset_y = spacing * math.cos(angle_radians)
    
    # Calculate baseline start and end points
    if angle_degrees == 0:
        start_x, start_y = 0, height
        end_x, end_y = width, height
    elif angle_degrees == 90:
        start_x, start_y = 0, 0
        end_x, end_y = 0, height
    elif angle_degrees == 180:
        start_x, start_y = width, 0
        end_x, end_y = 0, 0
    elif angle_degrees == 270:
        start_x, start_y = width, height
        end_x, end_y = width, 0
    else:
        start_x, start_y = 0, height
        end_x = width
        end_y = height - width * math.tan(angle_radians)
    
    # Apply scaling

    center_x = (start_x + end_x) / 2 
    center_y = (start_y + end_y) / 2
    start_x = center_x + (start_x - center_x) * scale_factor
    start_y = center_y + (start_y - center_y) * scale_factor
    end_x = center_x + (end_x - center_x) * scale_factor
    end_y = center_y + (end_y - center_y) * scale_factor
    
    # Generate lines
    num_lines = max(width, height) // (spacing // 2)
    lines = []
    for i in range(-num_lines, num_lines + 1):
        line_start_x = start_x + i * offset_x
        line_start_y = start_y + i * offset_y
        line_end_x = end_x + i * offset_x
        line_end_y = end_y + i * offset_y
        
        clipped_line = liang_barsky_clip(line_start_x, line_start_y, line_end_x, line_end_y, min_max_x_y_coord)
        if clipped_line:
            lines.append([
                np.array([round(clipped_line[0]), round(clipped_line[1])]),
                np.array([round(clipped_line[2]), round(clipped_line[3])])
            ])
       
    return lines

# Keeps the value within the allowed range
def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value, )

# Liang-Barsky algorithm for cutting lines within an image frame.
def liang_barsky_clip(x1, y1, x2, y2, min_max_x_y_coord):
    x_min = min_max_x_y_coord[0] - 2
    y_min  = min_max_x_y_coord[1] - 2
    x_max = min_max_x_y_coord[2] + 2
    y_max = min_max_x_y_coord[3] + 2
    
    def clip(p, q, t0, t1):
        if p == 0:  # With parallel edge
            return (t0, t1) if q >= 0 else (None, None)
        t = q / p
        if p < 0:
            if t > t1:
                return None, None
            if t > t0:
                t0 = t
        else:
            if t < t0:
                return None, None
            if t < t1:
                t1 = t
        return t0, t1

    dx = x2 - x1
    dy = y2 - y1
    t0, t1 = 0, 1

    t0, t1 = clip(-dx, x1 - x_min, t0, t1)
    if t0 is None: return None
    t0, t1 = clip(dx, x_max - x1, t0, t1)
    if t0 is None: return None
    t0, t1 = clip(-dy, y1 - y_min, t0, t1)
    if t0 is None: return None
    t0, t1 = clip(dy, y_max - y1, t0, t1)
    if t0 is None: return None

    new_x1 = x1 + t0 * dx
    new_y1 = y1 + t0 * dy
    new_x2 = x1 + t1 * dx
    new_y2 = y1 + t1 * dy

    return round(new_x1), round(new_y1), round(new_x2), round(new_y2)

# Bresenham's algorithms 
def bresenham(x1, y1, x2, y2):
    points = []
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    while True:
        points.append((x1, y1))
        
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    
    return np.array(points)
