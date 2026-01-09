from time import process_time
import heapq
from graph.map import Map
from search.SearchResult import SearchResult
from utils import horaSimuladaAtual

def ucs_search(map_graph: Map, start_name: str, end_name: str, *args, **kwargs) -> SearchResult:
    start_time = process_time()

    hora_atual = horaSimuladaAtual()
    
    start_node = map_graph.get_place(start_name)
    end_node = map_graph.get_place(end_name)

    if start_node is None or end_node is None:
        time_taken = process_time() - start_time
        return SearchResult(None, 0, 0, time_taken)

    if start_node == end_node:
        time_taken = process_time() - start_time
        return SearchResult([start_node], 0, 1, time_taken)

    pq = []
    heapq.heappush(pq, (0, id(start_node), start_node))
    
    parents = {start_node: start_node}
    g = {start_node: 0}

    visited = set()

    while pq:
        cost, _, current_node = heapq.heappop(pq)

        if current_node == end_node:
            reconst_path = []
            while parents[current_node] != current_node:
                reconst_path.append(current_node)
                current_node = parents[current_node]
            reconst_path.append(start_node)
            reconst_path.reverse()

            time_taken = process_time() - start_time
            
            total_dist = map_graph.calc_total_distance(reconst_path)
            
            return SearchResult(reconst_path, total_dist, len(visited), time_taken)

        if current_node in visited:
            continue
        visited.add(current_node)

        for (neighbor, zona, _) in map_graph.get_neighbours(current_node):
            edge_cost = map_graph.get_cost(current_node, neighbor, zona, hora_atual)
            new_cost = cost + edge_cost

            if neighbor not in visited:
                
                if new_cost < g.get(neighbor, float('inf')):
                    g[neighbor] = new_cost
                    parents[neighbor] = current_node
                    heapq.heappush(pq, (new_cost, id(neighbor), neighbor))

    time_taken = process_time() - start_time
    return SearchResult(None, 0, len(visited), time_taken)
