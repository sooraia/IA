from time import time
from graph.map import Map, Place, PlaceType, get_street_distance
from SearchResult import SearchResult

# Procura em profundidade com limite de profundidade
def dfs_depth(self, map: Map, start_name: str, target_name: str, max_depth: int, path = None, visited = None, current_depth = 0) -> SearchResult:
    if visited is None:
        visited = set()
    if path is None:
            path = []

    if max_depth < 0 or current_depth >= max_depth:
        return None
    
    start_place = map.get_place(start_name)
    if start_place is None:
        return None
    target_place = map.get_place(target_name)
    
    path = path + [start_place]

    if start_place == target_place:
        total_distance = 0
        for i in range(len(path) - 1):
            for neighbor in map.get_neighbors(path[i]):
                if neighbor == path[i+1]:
                    cost = map.get_street_distance(neighbor,path[i])
                    total_distance += cost
                    break
        return SearchResult(path.copy(), total_distance, visited.copy(), 0)
    
    visited.add(start_place)

    for neighbor in map.get_neighbors(start_place):
        if neighbor not in visited:
            result = self.dfs_depth(neighbor.get_name(), target_name, max_depth, path, visited, current_depth + 1)
            if result is not None:
                return result

    path.pop()
    return None

# Procura iterativa em profundidade
def iterative(self, map: Map, start_name: str, target_name: str) -> SearchResult:
    total_nodes = len(map.get_all_places()) #(máximo de profundidade - n-1 arestas)
    start = time.process_time()
    max_depth = 0
    while True:
        results = self.dfs_depth(map,start_name, target_name, max_depth)
        if results is not None:
            results.time_taken = time.process_time() - start
            return results
        
        if max_depth >= total_nodes:
            return SearchResult(
                None, None, None,
                time.process_time() - start
            )
         
        max_depth += 1
