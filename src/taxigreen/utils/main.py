from map import Map
from place import Place, PlaceType
from src.taxigreen.search.Graph import bfs
from src.taxigreen.search.DFS import dfs_search


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
    map_graph.add_edge("R1", "G1", 1.5)
    map_graph.add_edge("R1", "R3", 2.05)
    map_graph.add_edge("R1", "R5", 2.65)
    map_graph.add_edge("R1", "G3", 2.08)

    map_graph.add_edge("G1", "R2", 2.75)
    map_graph.add_edge("G1", "R4", 5.55)
    map_graph.add_edge("G1", "E1", 2.3)
    map_graph.add_edge("G1", "R5", 2.45)

    map_graph.add_edge("R2", "R4", 4.3)
    map_graph.add_edge("R2", "R8", 4.2)
    map_graph.add_edge("R2", "E1", 1.9)
    map_graph.add_edge("R2", "R5", 2.45)

    map_graph.add_edge("R4", "R5", 4.35)
    map_graph.add_edge("R4", "E1", 3.85)
    map_graph.add_edge("R4", "R8", 2.5)
    map_graph.add_edge("R4", "G4", 1.0)

    map_graph.add_edge("G4", "R8", 1.7)
    map_graph.add_edge("G4", "R13", 3.35)
    map_graph.add_edge("G4", "R12", 2.75)

    map_graph.add_edge("R12", "R13", 2.0)
    map_graph.add_edge("R12", "G5", 2.1)

    map_graph.add_edge("R17", "R18", 1.0)
    map_graph.add_edge("R17", "G5", 1.8)

    map_graph.add_edge("R18", "G5", 2.8)
    map_graph.add_edge("R18", "R9", 3.45)
    map_graph.add_edge("R18", "R19", 1.15)

    map_graph.add_edge("E3", "R19", 1.1)
    map_graph.add_edge("E3", "R15", 3.15)
    map_graph.add_edge("E3", "R20", 0.55)

    map_graph.add_edge("R20", "R21", 2.15)

    map_graph.add_edge("R21", "R15", 1.9)
    map_graph.add_edge("R21", "G6", 1.5)

    map_graph.add_edge("G6", "R16", 1.55)
    map_graph.add_edge("G6", "R15", 1.55)
    map_graph.add_edge("G6", "R11", 1.9)

    map_graph.add_edge("R16", "R11", 1.95)
    map_graph.add_edge("R16", "R7", 2.3)

    map_graph.add_edge("R7", "E2", 0.5)

    map_graph.add_edge("G2", "E2", 1.95)
    map_graph.add_edge("G2", "R11", 2.75)
    map_graph.add_edge("G2", "R3", 1.5)
    map_graph.add_edge("G2", "R6", 2.95)

    map_graph.add_edge("R3", "R5", 3.5)
    map_graph.add_edge("R3", "R6", 1.45)

    map_graph.add_edge("R5", "E1", 1.15)
    map_graph.add_edge("R5", "G3", 1.85)
    map_graph.add_edge("R5", "R6", 2.8)

    map_graph.add_edge("R6", "E1", 2.95)
    map_graph.add_edge("R6", "G3", 1.95)
    map_graph.add_edge("R6", "R15", 3.15)
    map_graph.add_edge("R6", "R11", 2.8)
    map_graph.add_edge("R6", "E2", 2.0)

    map_graph.add_edge("G3", "E1", 2.0)
    map_graph.add_edge("G3", "R10", 1.05)

    map_graph.add_edge("E1", "R8", 3.1)
    map_graph.add_edge("E1", "R9", 2.8)
    map_graph.add_edge("E1", "R14", 3.55)
    map_graph.add_edge("E1", "R10", 2.6)

    map_graph.add_edge("R11", "E2", 1.8)
    map_graph.add_edge("R11", "R10", 2.95)
    map_graph.add_edge("R11", "R15", 3.1)

    map_graph.add_edge("R10", "R8", 2.9)
    map_graph.add_edge("R10", "R9", 2.65)
    map_graph.add_edge("R10", "R14", 2.75)
    map_graph.add_edge("R10", "R15", 3.05)

    map_graph.add_edge("R15", "R9", 4.45)
    map_graph.add_edge("R15", "R14", 2.35)
    map_graph.add_edge("R15", "R19", 2.85)

    map_graph.add_edge("R14", "R19", 1.8)
    map_graph.add_edge("R14", "G5", 2.55)
    map_graph.add_edge("R14", "R13", 2.55)
    map_graph.add_edge("R14", "R9", 2.6)

    map_graph.add_edge("R9", "G5", 2.65)
    map_graph.add_edge("R9", "R13", 2.75)
    map_graph.add_edge("R9", "R8", 1.25)

    map_graph.add_edge("G5", "R13", 1.5)
    map_graph.add_edge("G5", "R19", 2.35)

    map_graph.add_edge("R13", "R8", 2.45)
    map_graph.add_edge("R13", "R19", 3.75)

    # ---------- Teste rápido ----------
    # print("Nós criados (primeiros 10):")
    # for p in map_graph.places[:10]:
    #     print(f"ID: {p.get_id():2d}  |  Nome: {p.get_name()}")

    # print("\nGrafo (primeiras linhas):")
    # print(map_graph)

    # print("\nTodas as arestas:")
    # print(map_graph.imprime_aresta())

    # testar bfs
    
    # origem = "R3"
    # destino = "G5"
    
    # print(f"\n--- A testar BFS de {origem} para {destino} ---")
    
    # caminho_resultado = bfs(map_graph, origem, destino)
    
    # if caminho_resultado:
        # print("✅ Sucesso! Caminho encontrado:")
        # print(caminho_resultado)
    # else:
        # print("❌ Caminho não encontrado.")
    # -------------
    
    return map_graph


if __name__ == "__main__":
    main()

    map_graph_instance = main()

    print("\n--- Teste de Busca em Profundidade (DFS) de R1 para E3 ---")
    caminho_encontrado = dfs_search(map_graph_instance, "R1", "E3")

    if caminho_encontrado:
        print(f"caminho: {caminho_encontrado}")
        print(f"O custo total deste caminho é: {map_graph_instance.calc_total_cost(caminho_encontrado)}")
    else:
        print("Caminho de R1 para E3 não encontrado.")


"""if __name__ == "__main__":
    main()"""