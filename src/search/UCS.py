from time import process_time
import heapq
from graph.map import Map
from search.SearchResult import SearchResult
from src.utils import horaSimuladaAtual
from domain.state import get_fator_transito

def ucs_search(map_graph: Map, start_name: str, end_name: str) -> SearchResult:
    start_time = process_time()

    hora_atual = horaSimuladaAtual()

    # Converter as strings em objetos 'Place'
    start_node = map_graph.get_place(start_name)
    end_node = map_graph.get_place(end_name)

    # verificar se os nodos existem no grafo
    if start_node is None or end_node is None:
        time_taken = process_time() - start_time
        return SearchResult(None, 0, set(), time_taken)

    # se o inicio é igual ao fim
    if start_node == end_node:
        time_taken = process_time() - start_time
        return SearchResult([start_node], 0, {start_node}, time_taken)

    # Fila de prioridade: (custo, id, no_atual, caminho)
    pq = []
    heapq.heappush(pq, (0, id(start_node), start_node, [start_node]))

    visited = set()

    while pq:
        cost, _, current_node, path = heapq.heappop(pq)

        # Se chegámos ao destino
        if current_node == end_node:
            time_taken = process_time() - start_time
            return SearchResult(path, cost, visited, time_taken)

        if current_node in visited:
            continue
        visited.add(current_node)

        # Explorar vizinhos
        for (neighbor, dist, zona) in map_graph.get_neighbours(current_node):

            if neighbor not in visited:
                transito = get_fator_transito(zona, hora_atual)
                weight = dist * transito
                new_cost = cost + weight
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_cost, id(neighbor), neighbor, new_path))

    # Se nao encontrou caminho
    time_taken = process_time() - start_time
    return SearchResult(None, 0, visited, time_taken)
