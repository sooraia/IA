from time import process_time
import heapq
from graph.map import Map
from search.SearchResult import SearchResult
from utils import horaSimuladaAtual

def ucs_search(map_graph: Map, start_name: str, end_name: str, *args, **kwargs) -> SearchResult:
    start_time = process_time()

    hora_atual = horaSimuladaAtual()

    # Converter as strings em objetos 'Place'
    start_node = map_graph.get_place(start_name)
    end_node = map_graph.get_place(end_name)

    # verificar se os nodos existem no grafo
    if start_node is None or end_node is None:
        time_taken = process_time() - start_time
        return SearchResult(None, 0, 0, time_taken)

    # se o inicio é igual ao fim
    if start_node == end_node:
        time_taken = process_time() - start_time
        return SearchResult([start_node], 0, 1, time_taken)

    # Fila de prioridade: (custo, id, no_atual)
    pq = []
    heapq.heappush(pq, (0, id(start_node), start_node))
    
    # Dicionários para reconstrução do caminho e custo
    parents = {start_node: start_node}
    g = {start_node: 0} # custom g (custo acumulado)

    visited = set()

    while pq:
        cost, _, current_node = heapq.heappop(pq)

        # Se chegámos ao destino
        if current_node == end_node:
            reconst_path = []
            while parents[current_node] != current_node:
                reconst_path.append(current_node)
                current_node = parents[current_node]
            reconst_path.append(start_node)
            reconst_path.reverse()

            time_taken = process_time() - start_time
            
            # Calcular a distancia fisica real para o resultado (consistente com outros algoritmos)
            total_dist = map_graph.calc_total_distance(reconst_path)
            
            return SearchResult(reconst_path, total_dist, len(visited), time_taken)

        if current_node in visited:
            continue
        visited.add(current_node)

        # Explorar vizinhos
        for (neighbor, zona, _) in map_graph.get_neighbours(current_node):
            edge_cost = map_graph.get_cost(current_node, neighbor, zona, hora_atual)
            new_cost = cost + edge_cost

            if neighbor not in visited:
                # Se encontrarmos um caminho melhor para o vizinho
                if new_cost < g.get(neighbor, float('inf')):
                    g[neighbor] = new_cost
                    parents[neighbor] = current_node
                    heapq.heappush(pq, (new_cost, id(neighbor), neighbor))

    # Se nao encontrou caminho
    time_taken = process_time() - start_time
    return SearchResult(None, 0, len(visited), time_taken)
