from time import process_time
from graph.map import Map
from search.SearchResult import SearchResult

def a_star_search(map_graph: Map, start_name, target_name, heuristic_func) -> SearchResult:
    start_time = process_time()

    start = map_graph.get_place(start_name)
    target = map_graph.get_place(target_name)
    g = {}
    g[start] = 0
    
    open_list = set([start])     #lista de nós visitados mas com vizinhos não visitados
    closed_list = set([])          #lista de nós visitados
    
    parents = {}
    parents[start] = start
    
    while len(open_list) > 0:
        n = None
        
        for v in open_list:
            if n == None or g[v] + heuristic_func(v, target) < g[n] + heuristic_func(n, target):
                n = v
                
        if n == None:
            print("Path does not exist!")
            time_taken = process_time() - start_time
            return SearchResult(None, 0, closed_list, time_taken)
        
        if n == target:
            reconst_path = []
            while parents[n] != n:
                reconst_path.append(n)
                n = parents[n]
                
            reconst_path.append(start)
            reconst_path.reverse()
            
            print('Caminho encontrado: {}'.format(reconst_path))
            print('Custo do caminho: {}'.format(map_graph.calc_total_cost(reconst_path)))
            
            time_taken = process_time() - start_time
            total_cost = map_graph.calc_total_cost(reconst_path)
            return SearchResult(reconst_path, total_cost, closed_list, time_taken)

        for (m, weight) in map_graph.get_neighbours(n):
            if m not in open_list and m not in closed_list:
                open_list.add(m)
                parents[m] = n
                g[m] = g[n] + weight

            else:
                if g[m] > g[n] + weight:
                    g[m] = g[n] + weight
                    parents[m] = n

                    if m in closed_list:
                        closed_list.remove(m)
                        open_list.add(m)

        open_list.remove(n)
        closed_list.add(n)

    print('Caminho não existe!')
    time_taken = process_time() - start_time
    return SearchResult(None, 0, closed_list, time_taken)