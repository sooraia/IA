def dfs_search(map_graph, start_node_name, target_node_name):
    start_node = map_graph.get_place(start_node_name)
    target_node = map_graph.get_place(target_node_name)

    if start_node is None or target_node is None:
        return

    stack = [(start_node,[start_node])]
    visitados = {start_node}

    while stack:
        (current_node, path) = stack.pop(0)

        if current_node == target_node:
            return path

        neighbours = map_graph.get_neighbours(current_node)

        for neighbour, _ in neighbours:
            if neighbour not in visitados:
                visitados.add(neighbour)
                new_path = path + [neighbour]
                stack.append((neighbour, new_path))
    return None

