from datetime import time
import datetime
import sys
import os
from utils import set_hora_real_inicial
from domain.state import Estado

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from graph.map import Map
from graph.place import Place, PlaceType
from search.BFS import bfs_search
from search.DFS import dfs_search



def build_map():
    map_graph = Map()
    N_PONTOS_RECOLHA = 21
    N_POSTOS_ABASTECIMENTO = 6
    N_POSTOS_CARREGAMENTO = 3
    
    pontos_de_recolha_coords = [(4.7, 8.45), (1.8, 7.5), (6.15, 7.85), (0.0, 5.55), (3.85, 6.65), 
                                (6.1, 6.2), (8.65, 6.2), (1.7, 4.5), (2.55, 3.75), (4.75, 4.5)
                                (7.6, 5.75), (0.0, 1.8), (1.3, 2.5), (3.8,2.7), (6.0, 3.0), 
                                (8.6, 3.85), (2.1, 0.0), (3.25, 0.65), (4.14, 1.4), (5.15, 0.1), 
                                (6.8, 1.55)]
    postos_de_abastecimento_coords = [(3.2, 8.45), (7.65, 7.6), (4.75,5.6), (0, 4.5), (2.1, 1.8), (7.65, 2.8)]
    postos_de_carregamento_coords = [(3.2, 6.15), (8.1, 6.2), (4.9, 0.6)]
    ## ADICIONAR CENTRAL

    """ Add nodes to map graph """
    #   Pontos de recolha
    for i in range (N_PONTOS_RECOLHA):
        map_graph.add_place(PlaceType.RECOLHA_DE_PASSAGEIROS, pontos_de_recolha_coords[i])

    #   Postos de Abastecimento
    for i in range (N_POSTOS_ABASTECIMENTO):
        map_graph.add_place(PlaceType.POSTO_DE_ABASTECIMENTO, postos_de_abastecimento_coords[i])

    #   Estações de carga
    for i in range (N_POSTOS_CARREGAMENTO):
        map_graph.add_place(PlaceType.ESTACAO_DE_CARGA, postos_de_carregamento_coords[i])

    """ Add edges to map graph """
    map_graph.add_edge("R1", "G1")
    map_graph.add_edge("R1", "R3")
    map_graph.add_edge("R1", "R5")
    map_graph.add_edge("R1", "G3")

    map_graph.add_edge("G1", "R2")
    map_graph.add_edge("G1", "R4")
    map_graph.add_edge("G1", "E1")
    map_graph.add_edge("G1", "R5")

    map_graph.add_edge("R2", "R4")
    map_graph.add_edge("R2", "R8")
    map_graph.add_edge("R2", "E1")
    map_graph.add_edge("R2", "R5")

    map_graph.add_edge("R4", "R5")
    map_graph.add_edge("R4", "E1")
    map_graph.add_edge("R4", "R8")
    map_graph.add_edge("R4", "G4")

    map_graph.add_edge("G4", "R8")
    map_graph.add_edge("G4", "R13")
    map_graph.add_edge("G4", "R12")

    map_graph.add_edge("R12", "R13")
    map_graph.add_edge("R12", "G5")

    map_graph.add_edge("R17", "R18")
    map_graph.add_edge("R17", "G5")

    map_graph.add_edge("R18", "G5")
    map_graph.add_edge("R18", "R9")
    map_graph.add_edge("R18", "R19")

    map_graph.add_edge("E3", "R19")
    map_graph.add_edge("E3", "R15")
    map_graph.add_edge("E3", "R20")

    map_graph.add_edge("R20", "R21")

    map_graph.add_edge("R21", "R15")
    map_graph.add_edge("R21", "G6")

    map_graph.add_edge("G6", "R16")
    map_graph.add_edge("G6", "R15")
    map_graph.add_edge("G6", "R11")

    map_graph.add_edge("R16", "R11")
    map_graph.add_edge("R16", "R7")

    map_graph.add_edge("R7", "E2")

    map_graph.add_edge("G2", "E2")
    map_graph.add_edge("G2", "R11")
    map_graph.add_edge("G2", "R3")
    map_graph.add_edge("G2", "R6")

    map_graph.add_edge("R3", "R5")
    map_graph.add_edge("R3", "R6")

    map_graph.add_edge("R5", "E1")
    map_graph.add_edge("R5", "G3")
    map_graph.add_edge("R5", "R6")

    map_graph.add_edge("R6", "E1")
    map_graph.add_edge("R6", "G3")
    map_graph.add_edge("R6", "R15")
    map_graph.add_edge("R6", "R11")
    map_graph.add_edge("R6", "E2")

    map_graph.add_edge("G3", "E1")
    map_graph.add_edge("G3", "R10")

    map_graph.add_edge("E1", "R8")
    map_graph.add_edge("E1", "R9")
    map_graph.add_edge("E1", "R14")
    map_graph.add_edge("E1", "R10")

    map_graph.add_edge("R11", "E2")
    map_graph.add_edge("R11", "R10")
    map_graph.add_edge("R11", "R15")

    map_graph.add_edge("R10", "R8")
    map_graph.add_edge("R10", "R9")
    map_graph.add_edge("R10", "R14")
    map_graph.add_edge("R10", "R15")

    map_graph.add_edge("R15", "R9")
    map_graph.add_edge("R15", "R14")
    map_graph.add_edge("R15", "R19")

    map_graph.add_edge("R14", "R19")
    map_graph.add_edge("R14", "G5")
    map_graph.add_edge("R14", "R13")
    map_graph.add_edge("R14", "R9")

    map_graph.add_edge("R9", "G5")
    map_graph.add_edge("R9", "R13")
    map_graph.add_edge("R9", "R8")

    map_graph.add_edge("G5", "R13")
    map_graph.add_edge("G5", "R19")

    map_graph.add_edge("R13", "R8")
    map_graph.add_edge("R13", "R19")

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

    map_graph_instance = build_map()
    set_hora_real_inicial(datetime.now)
    # ... estado
    


"""if __name__ == "__main__":
    main()"""