from collections import deque
from time import process_time
from graph.map import Map
from search.SearchResult import SearchResult

def bfs_search(map_graph: Map, start_name: str, end_name: str) -> SearchResult:
    start_time = process_time()
    # Converter as strings em objetos 'Place'
    start = map_graph.get_place(start_name)
    end = map_graph.get_place(end_name)
    # verificar se os nodos existem no grafo
    if start is None or end is None:
        time_taken = process_time() - start_time
        return SearchResult(None, 0, set(), time_taken) # set() cria um conjunto vazio q n pode ter duplicados
    
    # se o inicio é igual ao fim
    if start == end:
        time_taken = process_time() - start_time
        return SearchResult([start], 0, {start}, time_taken) # {start} cria um conjunto com o node start
    
    # criar a fila para guardar os nós que vamos visitar
    queue = deque()
    queue.append([start])

    # guardar o caminho
    visited = set()
    visited.add(start)

    while queue: # enquanto a fila nao estiver vazia
        # Retira o primeiro caminho da fila (FIFO)
        path = queue.popleft()
        current_node = path[-1] # Último nodo do caminho
        
        # Explorar os vizinhos do nodo atual
        for (neighbor,_,_) in map_graph.get_neighbours(current_node):
            if neighbor not in visited:
                # Criar novo caminho incluindo o vizinho
                new_path = path + [neighbor]

                # Se chegámos ao destino, retornar o caminho
                if neighbor == end:
                    total_cost = map_graph.calc_total_distance(new_path)
                    time_taken = process_time() - start_time
                    return SearchResult(new_path, total_cost, visited, time_taken)
                
                # Adicionar o novo caminho à fila e marcar como visitado
                queue.append(new_path)
                visited.add(neighbor)
    # Se nao encontrou caminho
    time_taken = process_time() - start_time
    return SearchResult(None, 0, visited, time_taken)
                