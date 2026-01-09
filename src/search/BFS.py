from collections import deque
from time import process_time
from graph.map import Map
from search.SearchResult import SearchResult

def bfs_search(map_graph: Map, start_name: str, end_name: str, *args, **kwargs) -> SearchResult:
    start_time = process_time()
    
    start = map_graph.get_place(start_name)
    end = map_graph.get_place(end_name)
    
    if start is None or end is None:
        time_taken = process_time() - start_time
        return SearchResult(None, 0, 0, time_taken)
    
    if start == end:
        time_taken = process_time() - start_time
        return SearchResult([start], 0, 1, time_taken)
    
    queue = deque()
    queue.append([start])

    visited = set()
    visited.add(start)

    while queue: 
        path = queue.popleft()
        current_node = path[-1]
        for (neighbor, _, _) in map_graph.get_neighbours(current_node):
            if neighbor not in visited:
                new_path = path + [neighbor]

                if neighbor == end:
                    total_cost = map_graph.calc_total_distance(new_path)
                    time_taken = process_time() - start_time
                    return SearchResult(new_path, total_cost, len(visited), time_taken)
                
                queue.append(new_path)
                visited.add(neighbor)
    time_taken = process_time() - start_time
    return SearchResult(None, 0, len(visited), time_taken)
                