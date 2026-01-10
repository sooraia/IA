from graph.map import Map
from time import process_time
from search.SearchResult import SearchResult

def dfs_search(map_graph : Map, start_node_name, target_node_name, *args) -> SearchResult:
    start_time = process_time()
    
    start_node = map_graph.get_place(start_node_name)
    target_node = map_graph.get_place(target_node_name)

    if start_node is None or target_node is None:
        time_taken = process_time() - start_time
        return SearchResult(None, 0, 0, time_taken)

    stack = [(start_node,[start_node])]
    visitados = {start_node}

    while stack:
        (current_node, path) = stack.pop() 

        if current_node == target_node:
            total_cost = map_graph.calc_total_distance(path)
            time_taken = process_time() - start_time
            return SearchResult(path, total_cost, len(visitados), time_taken)

        neighbours = map_graph.get_neighbours(current_node)

        for (neighbour,_,_)in neighbours:
            if neighbour not in visitados:
                visitados.add(neighbour)
                new_path = path + [neighbour]
                stack.append((neighbour, new_path))
    
    time_taken = process_time() - start_time
    return SearchResult(None, 0, len(visitados), time_taken)

