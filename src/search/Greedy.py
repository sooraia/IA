from time import process_time
from graph.map import Map
from search.SearchResult import SearchResult

def greedy_search(map_graph: Map, start_name: str, target_name: str, vehicle, heuristic) -> SearchResult:
    start_time = process_time()
    start = map_graph.get_place(start_name)
    target = map_graph.get_place(target_name)

    open_list = set([start])     #lista de nós visitados mas com vizinhos não visitados
    visited_list = set([])          #lista de nós visitados

    parents = {}
    parents[start] = start

    while len(open_list) > 0:
        n = None

        # encontrar o nó na open_list com menor heurística
        for v in open_list:
            if n == None or heuristic(v, target, vehicle) < heuristic(n, target, vehicle):
                n = v
        
        if n == None:
            time_taken = process_time() - start_time
            return SearchResult(None, 0, len(visited_list), time_taken)
        
        # se chegámos ao destino
        if n == target:
            reconst_path = []

            # reconstroi o caminho de tras para a frente
            while parents[n] != n:
                reconst_path.append(n)
                n = parents[n]
                
            reconst_path.append(start)

            reconst_path.reverse() # inverte para ficar Inicio -> Fim
            
            total_cost = map_graph.calc_total_distance(reconst_path)
            time_taken = process_time() - start_time
            return SearchResult(reconst_path, total_cost, len(visited_list), time_taken)
        
        for (m,_,_) in map_graph.get_neighbours(n):
            if m not in open_list and m not in visited_list:
                open_list.add(m)
                parents[m] = n
        
        open_list.remove(n)
        visited_list.add(n)

    time_taken = process_time() - start_time
    return SearchResult(None, 0, len(visited_list), time_taken)