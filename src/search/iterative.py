from time import process_time
from graph.map import Map, Place, PlaceType
from search.SearchResult import SearchResult
from src.utils import horaSimuladaAtual

# Procura em profundidade com limite de profundidade
def dfs_depth(map_graph: Map, start_name: str, target_name: str, max_depth: int, path=None, visited=None, current_depth=0, distance_atual=0) -> SearchResult:
    if visited is None:
        visited = set()
    if path is None:
        path = []

    if max_depth < 0 or current_depth >= max_depth:
        return SearchResult(None, 0, len(visited), 0)
    
    start_place = map_graph.get_place(start_name)
    if start_place is None:
        return SearchResult(None, 0, len(visited), 0)
    target_place = map_graph.get_place(target_name)
    
    path.append(start_place)
    visited.add(start_place)

    if start_place == target_place:
        result = SearchResult(path.copy(), distance_atual, len(visited), 0)
        path.pop()
        visited.discard(start_place)
        return result
    
    visited.add(start_place)

    for (neighbor, place_type, _) in map_graph.get_neighbours(start_place):
        if neighbor not in visited:
            distance = map_graph.get_distancia_rota(start_place, neighbor)
            result = dfs_depth(map_graph, neighbor.get_name(), target_name, max_depth, path, visited, current_depth + 1, distance_atual + distance)
            if result.path is not None:
                path.pop()
                visited.discard(start_place)
                return result

    visited.discard(start_place)
    path.pop()
    return SearchResult(None, 0, len(visited), 0)

# Procura iterativa em profundidade
def iterative(map_graph: Map, start_name: str, target_name: str, *args, **kwargs) -> SearchResult:
    total_nodes = len(map_graph.places) #(máximo de profundidade - n-1 arestas)
    start = process_time()
    max_depth = 0
    visited = 0
    while True:
        results = dfs_depth(map_graph, start_name, target_name, max_depth)
        if results.path is not None:
            results.time_taken = process_time() - start
            results.visited += visited
            return results
        else:
            visited += results.visited
        
        if max_depth >= total_nodes:
            return SearchResult(
                None, None, visited,
                process_time() - start
            )
         
        max_depth += 1
