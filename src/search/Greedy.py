def greedy_search(mapa, start_name, end_name):
    start = mapa.get_place(start_name)
    end = mapa.get_place(end_name)

    open_list = set([start])     #lista de nós visitados mas com vizinhos não visitados
    visited_list = set([])          #lista de nós visitados

    parents = {}
    parents[start] = start

    while len(open_list) > 0:
        n = None

        # encontrar o nó na open_list com menor heurística
        for v in open_list:
            if n == None or heuristic(v, end, vehicle) < heuristic(n, end, vehicle):
                n = v
        
        if n == None:
            print("Path does not exist")
            return None
        
        # se chegámos ao destino
        if n == end:
            reconst_path = []

            # reconstroi o caminho de tras para a frente
            while parents[n] != n:
                reconst_path.append(n)
                n = parents[n]
                
            reconst_path.append(start)

            reconst_path.reverse() # inverte para ficar Inicio -> Fim
            
            return (reconst_path, mapa.calc_total_cost(reconst_path))
        
        for (m, weight) in mapa.get_neighbours(n):
            if m not in open_list and m not in visited_list:
                open_list.add(m)
                parents[m] = n
        
        open_list.remove(n)
        visited_list.add(n)

    print("Path does not exist")
    return None