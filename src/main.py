import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from graph.map import Map
from graph.place import Place, PlaceType
from search.BFS import bfs_search
from search.DFS import dfs_search



def main():
    map_graph = Map()
    N_PONTOS_RECOLHA = 21
    N_POSTOS_ABASTECIMENTO = 6
    N_POSTOS_CARREGAMENTO = 3

    ## ADICIONAR CENTRAL

    """ Add nodes to map graph """
    #   Pontos de recolha
    for i in range (N_PONTOS_RECOLHA):
        map_graph.add_place(PlaceType.RECOLHA_DE_PASSAGEIROS)

    #   Postos de Abastecimento
    for i in range (N_POSTOS_ABASTECIMENTO):
        map_graph.add_place(PlaceType.POSTO_DE_ABASTECIMENTO)

    #   Estações de carga
    for i in range (N_POSTOS_CARREGAMENTO):
        map_graph.add_place(PlaceType.ESTACAO_DE_CARGA)

    """ Add edges to map graph """
    map_graph.add_edge("R1", "G1", 1.5, "Normal")
    map_graph.add_edge("R1", "R3", 2.05, "Residencial")
    map_graph.add_edge("R1", "R5", 2.65, "Normal")
    map_graph.add_edge("R1", "G3", 2.08, "Residencial")

    map_graph.add_edge("G1", "R2", 2.75, "Normal")
    map_graph.add_edge("G1", "R4", 5.55, "Normal")
    map_graph.add_edge("G1", "E1", 2.3, "Normal")
    map_graph.add_edge("G1", "R5", 2.45, "Normal")

    map_graph.add_edge("R2", "R4", 4.3, "Normal")
    map_graph.add_edge("R2", "R8", 4.2, "Normal")
    map_graph.add_edge("R2", "E1", 1.9, "Normal")
    map_graph.add_edge("R2", "R5", 2.45, "Normal")

    map_graph.add_edge("R4", "R5", 4.35, "Normal")
    map_graph.add_edge("R4", "E1", 3.85, "Normal")
    map_graph.add_edge("R4", "R8", 2.5, "Normal")
    map_graph.add_edge("R4", "G4", 1.0, "Normal")

    map_graph.add_edge("G4", "R8", 1.7, "Normal")
    map_graph.add_edge("G4", "R13", 3.35, "Normal")
    map_graph.add_edge("G4", "R12", 2.75, "Normal")

    map_graph.add_edge("R12", "R13", 2.0, "Normal")
    map_graph.add_edge("R12", "G5", 2.1, "Normal")

    map_graph.add_edge("R17", "R18", 1.0, "Normal")
    map_graph.add_edge("R17", "G5", 1.8, "Normal")

    map_graph.add_edge("R18", "G5", 2.8, "Normal")
    map_graph.add_edge("R18", "R9", 3.45, "Normal")
    map_graph.add_edge("R18", "R19", 1.15, "Old town")

    map_graph.add_edge("E3", "R19", 1.1, "Old town")
    map_graph.add_edge("E3", "R15", 3.15, "Old town")
    map_graph.add_edge("E3", "R20", 0.55, "Old town")

    map_graph.add_edge("R20", "R21", 2.15, "Old town")

    map_graph.add_edge("R21", "R15", 1.9, "Old town")
    map_graph.add_edge("R21", "G6", 1.5, "Old town")

    map_graph.add_edge("G6", "R16", 1.55, "Old town")
    map_graph.add_edge("G6", "R15", 1.55, "Old town")
    map_graph.add_edge("G6", "R11", 1.9, "Old town")

    map_graph.add_edge("R16", "R11", 1.95, "Old town")
    map_graph.add_edge("R16", "R7", 2.3, "Old town")

    map_graph.add_edge("R7", "E2", 0.5, "Residencial")

    map_graph.add_edge("G2", "E2", 1.95, "Residencial")
    map_graph.add_edge("G2", "R11", 2.75, "Residencial")
    map_graph.add_edge("G2", "R3", 1.5, "Residencial")
    map_graph.add_edge("G2", "R6", 2.95, "Residencial")

    map_graph.add_edge("R3", "R5", 3.5, "Residencial")
    map_graph.add_edge("R3", "R6", 1.45, "Residencial")

    map_graph.add_edge("R5", "E1", 1.15, "Normal")
    map_graph.add_edge("R5", "G3", 1.85, "Residencial")
    map_graph.add_edge("R5", "R6", 2.8, "Residencial")

    map_graph.add_edge("R6", "E1", 2.95, "Residencial")
    map_graph.add_edge("R6", "G3", 1.95, "Residencial")
    map_graph.add_edge("R6", "R15", 3.15, "Residencial")
    map_graph.add_edge("R6", "R11", 2.8, "Residencial")
    map_graph.add_edge("R6", "E2", 2.0, "Residencial")

    map_graph.add_edge("G3", "E1", 2.0, "Residencial")
    map_graph.add_edge("G3", "R10", 1.05, "Residencial")

    map_graph.add_edge("E1", "R8", 3.1, "Normal")
    map_graph.add_edge("E1", "R9", 2.8, "Normal")
    map_graph.add_edge("E1", "R14", 3.55, "Old town")
    map_graph.add_edge("E1", "R10", 2.6, "Residencial")

    map_graph.add_edge("R11", "E2", 1.8, "Residencial")
    map_graph.add_edge("R11", "R10", 2.95, "Residencial")
    map_graph.add_edge("R11", "R15", 3.1, "Old town")

    map_graph.add_edge("R10", "R8", 2.9, "Residencial")
    map_graph.add_edge("R10", "R9", 2.65, "Residencial")
    map_graph.add_edge("R10", "R14", 2.75, "Residencial")
    map_graph.add_edge("R10", "R15", 3.05, "Residencial")

    map_graph.add_edge("R15", "R9", 4.45, "Old town")
    map_graph.add_edge("R15", "R14", 2.35, "Old town")
    map_graph.add_edge("R15", "R19", 2.85, "Old town")

    map_graph.add_edge("R14", "R19", 1.8, "Old town")
    map_graph.add_edge("R14", "G5", 2.55, "Old town")
    map_graph.add_edge("R14", "R13", 2.55, "Old town")
    map_graph.add_edge("R14", "R9", 2.6, "Old town")

    map_graph.add_edge("R9", "G5", 2.65, "Normal")
    map_graph.add_edge("R9", "R13", 2.75, "Normal")
    map_graph.add_edge("R9", "R8", 1.25, "Normal")

    map_graph.add_edge("G5", "R13", 1.5, "Normal")
    map_graph.add_edge("G5", "R19", 2.35, "Old town")

    map_graph.add_edge("R13", "R8", 2.45, "Normal")
    map_graph.add_edge("R13", "R19", 3.75, "Old town")

    # ---------- Teste rápido ----------
    # print("Nós criados (primeiros 10):")
    # for p in map_graph.places[:10]:
    #     print(f"ID: {p.get_id():2d}  |  Nome: {p.get_name()}")

    # print("\nGrafo (primeiras linhas):")
    # print(map_graph)

    # print("\nTodas as arestas:")
    # print(map_graph.imprime_aresta())

    
    return map_graph


if __name__ == "__main__":
    main()

    map_graph_instance = main()


    resultado_dfs = dfs_search(map_graph_instance, "R1", "E3")
    resultado_bfs = bfs_search(map_graph_instance, "R1", "E3")

    print("\n--- Teste de Busca em Profundidade (DFS) de R1 para E3 ---")
    if resultado_dfs.path is not None:
        # Converter objetos para nomes
        nomes_dfs = [p.get_name() for p in resultado_dfs.path]
        
        print(f"Caminho: {nomes_dfs}")
        print(f"Distância Total: {resultado_dfs.distance}")
        print(f"Tempo de Execução: {resultado_dfs.time_taken:.6f} segundos")
        print(f"Nós visitados: {len(resultado_dfs.visited)}")
    else:
        print("DFS: Caminho não encontrado.")
        print(f"Tempo gasto: {resultado_dfs.time_taken:.6f} segundos")



    print("\n--- Teste de Busca em Largura (BFS) de R1 para E3 ---")
    if resultado_bfs.path is not None:
        # Converter objetos para nomes
        nomes_bfs = [p.get_name() for p in resultado_bfs.path]
        
        print(f"Caminho: {nomes_bfs}")
        print(f"Distância Total: {resultado_bfs.distance}")
        print(f"Tempo de Execução: {resultado_bfs.time_taken:.6f} segundos")
        print(f"Nós visitados: {len(resultado_bfs.visited)}")
    else:
        print("BFS: Caminho não encontrado.")
        print(f"Tempo gasto: {resultado_bfs.time_taken:.6f} segundos")
