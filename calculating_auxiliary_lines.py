from calculation_of_intersection_points import calculate_distance, find_intersection_of_segments

# calculating_auxiliary_lines.py

# Creating nearborn list between  points 
#If there is a barrier between 2 points, there is no connection between them
def creating_nearborn_list(intersection_points, shapes):
    neighborhood_list = {}

    for group in range(len(intersection_points)):
        current_row = intersection_points[group]
        previous_row = intersection_points[group - 1] if group > 0 else []
        next_row = intersection_points[group + 1] if group < len(intersection_points) - 1 else []

        for i in range(0, len(current_row) - 1, 2):
            key1, key2 = tuple(current_row[i]), tuple(current_row[i + 1])
            neighbors_key1 = []
            neighbors_key2 = []
            for point in range(len(next_row)):
                inter1 = []
                for shape in range(len(shapes)):
                    for j in range(len(shapes[shape]) - 1):
                        inter1.append(find_intersection_of_segments(key1, next_row[point], shapes[shape][j], shapes[shape][j - 1]))
                if all(element is None for element in inter1):
                    neighbors_key1.append((tuple(next_row[point]), calculate_distance(key1, next_row[point])))
                inter2 = []
                for shape in range(len(shapes)):
                    for j in range(len(shapes[shape]) - 1):
                        inter2.append(find_intersection_of_segments(key2, next_row[point], shapes[shape][j], shapes[shape][j - 1]))
                if all(element is None for element in inter2):
                    neighbors_key2.append((tuple(next_row[point]), calculate_distance(key2, next_row[point])))
            for point in range(len(previous_row)):
                inter1 = []
                for shape in range(len(shapes)):
                    for j in range(len(shapes[shape]) - 1):
                        inter1.append(find_intersection_of_segments(key1, previous_row[point], shapes[shape][j], shapes[shape][j - 1]))
                if all(element is None for element in inter1):
                    neighbors_key1.append((tuple(previous_row[point]), calculate_distance(key1, previous_row[point])))
                inter2 = []
                for shape in range(len(shapes)):
                    for j in range(len(shapes[shape]) - 1):
                        inter2.append(find_intersection_of_segments(key2, previous_row[point], shapes[shape][j], shapes[shape][j - 1]))
                if all(element is None for element in inter2):
                    neighbors_key2.append((tuple(previous_row[point]), calculate_distance(key2, previous_row[point])))
            
            # Add point and distance
            neighbors_key1.insert(0, (tuple(key2), calculate_distance(key1, key2)))
            neighbors_key2.insert(0, (tuple(key1), calculate_distance(key2, key1)))

            neighborhood_list.setdefault(key1, []).extend(neighbors_key1)
            neighborhood_list.setdefault(key2, []).extend(neighbors_key2)

    return neighborhood_list

# Connecting sections by nearest point
def connecting_sections(neighborhood_list, first_point, second_point, visited_points):
    visited_points.append(first_point)  
    visited_points.append(second_point)  

    while first_point in neighborhood_list and neighborhood_list[first_point]:
        # We select the closest point that is not yet in the list
        closest_point = min(
            (point for point in neighborhood_list[second_point] if point[0] not in visited_points),
            key=lambda x: x[1], default=None
        )
        
        # If there are no more points that we haven't visited yet, we exit
        if closest_point is None:
            print("No new, not yet visited points, exit")
            break

        first_point = closest_point[0] 
        visited_points.append(first_point)  # Add the visited_points
        
        second_point = neighborhood_list[first_point][0][0]
        visited_points.append(second_point)
       
    
    return visited_points

# Heap sort up
def heapify_up(heap, index):
    parent = (index - 1) // 2
    while index > 0 and heap[index][0] < heap[parent][0]:
        heap[index], heap[parent] = heap[parent], heap[index]
        index = parent
        parent = (index - 1) // 2

# Heap sort down
def heapify_down(heap, index):
    smallest = index
    left = 2 * index + 1
    right = 2 * index + 2

    if left < len(heap) and heap[left][0] < heap[smallest][0]:
        smallest = left
    if right < len(heap) and heap[right][0] < heap[smallest][0]:
        smallest = right
    if smallest != index:
        heap[index], heap[smallest] = heap[smallest], heap[index]
        heapify_down(heap, smallest)

# Insert item
def push_heap(heap, item):
    heap.append(item)
    heapify_up(heap, len(heap) - 1)

# Remove item
def pop_heap(heap):
    if len(heap) == 1:
        return heap.pop()
    root = heap[0]
    heap[0] = heap.pop()
    heapify_down(heap, 0)
    return root

def dijkstra(neighborhood_list, start, end):
    pq = []  
    distances = {node: float('inf') for node in neighborhood_list}
    previous_nodes = {node: None for node in neighborhood_list}
    distances[start] = 0
    push_heap(pq, (0, start))

    while pq:
        curr_dist, curr_node = pop_heap(pq)

        if curr_node == end:
            break

        if curr_dist > distances[curr_node]:
            continue

        for neighbor, weight in neighborhood_list[curr_node]:
            distance = curr_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = curr_node
                push_heap(pq, (distance, neighbor))

    # Decrypt route
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous_nodes[node]
    path.reverse()

    return distances[end], path
