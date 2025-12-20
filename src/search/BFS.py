from collections import deque

def bfs_search(mapa, start_name, end_name):
    # Converter as strings em objetos 'Place'
    start = mapa.get_place(start_name)
    end = mapa.get_place(end_name)

    # verificar se os nodos existem no grafo
    if start is None or end is None:
        return None
    
    # se o inicio é igual ao fim
    if start == end:
        return [start]
    
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
                    return novo_caminho
                
                # Adicionar o novo caminho à fila e marcar como visitado
                fila.append(novo_caminho)
                visited.add(vizinho)

    # Se nao encontrou caminho
    return None
                