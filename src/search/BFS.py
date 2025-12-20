from collections import deque
from time import process_time
from graph.map import Map
from search.SearchResult import SearchResult

def bfs_search(mapa: Map, start_name, end_name) -> SearchResult:
    start_time = process_time()
    # Converter as strings em objetos 'Place'
    start = mapa.get_place(start_name)
    end = mapa.get_place(end_name)

    # verificar se os nodos existem no grafo
    if start is None or end is None:
        time_taken = process_time() - start_time
        return SearchResult(None, 0, set(), time_taken) # set() cria um conjunto vazio q n pode ter duplicados
    
    # se o inicio é igual ao fim
    if start == end:
        time_taken = process_time() - start_time
        return SearchResult([start], 0, {start}, time_taken) # {start} cria um conjunto com o node start
    
    # criar a fila para guardar os nós que vamos visitar
    fila = deque()
    fila.append([start])

    # guardar o caminho
    visited = set()
    visited.add(start)

    while fila: # enquanto a fila nao estiver vazia
        # Retira o primeiro caminho da fila (FIFO)
        caminho = fila.popleft()
        nodo_atual = caminho[-1] # Último nodo do caminho
        
        # Explorar os vizinhos do nodo atual
        for (vizinho, custo) in mapa.get_neighbours(nodo_atual):
            if vizinho not in visited:
                # Criar novo caminho incluindo o vizinho
                novo_caminho = caminho + [vizinho]

                # Se chegámos ao destino, retornar o caminho
                if vizinho == end:
                    custo_total = mapa.calc_total_cost(novo_caminho)
                    time_taken = process_time() - start_time
                    return SearchResult(novo_caminho, custo_total, visited, time_taken)
                
                # Adicionar o novo caminho à fila e marcar como visitado
                fila.append(novo_caminho)
                visited.add(vizinho)

    # Se nao encontrou caminho
    time_taken = process_time() - start_time
    return SearchResult(None, 0, visited, time_taken)
                