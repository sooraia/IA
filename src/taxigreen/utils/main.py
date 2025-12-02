from map import Map
from place import Place, PlaceType
from Graph import bfs


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
    map_graph.add_edge("R1", "G1", 1)
    map_graph.add_edge("R1", "R3", 1)
    map_graph.add_edge("R1", "R5", 1)
    map_graph.add_edge("R1", "G3", 1)

    map_graph.add_edge("G1", "R2", 1)
    map_graph.add_edge("G1", "R4", 1)
    map_graph.add_edge("G1", "E1", 1)
    map_graph.add_edge("G1", "R5", 1)

    map_graph.add_edge("R2", "R4", 1)
    map_graph.add_edge("R2", "R8", 1)
    map_graph.add_edge("R2", "E1", 1)
    map_graph.add_edge("R2", "R5", 1)

    map_graph.add_edge("R4", "R5", 1)
    map_graph.add_edge("R4", "E1", 1)
    map_graph.add_edge("R4", "R8", 1)
    map_graph.add_edge("R4", "G4", 1)

    map_graph.add_edge("G4", "R8", 1)
    map_graph.add_edge("G4", "R13", 1)
    map_graph.add_edge("G4", "R12", 1)

    map_graph.add_edge("R12", "R13", 1)
    map_graph.add_edge("R12", "G5", 1)

    map_graph.add_edge("R17", "R18", 1)
    map_graph.add_edge("R17", "G5", 1)

    map_graph.add_edge("R18", "G5", 1)
    map_graph.add_edge("R18", "R9", 1)
    map_graph.add_edge("R18", "R19", 1)

    map_graph.add_edge("E3", "R19", 1)
    map_graph.add_edge("E3", "R15", 1)
    map_graph.add_edge("E3", "R20", 1)

    map_graph.add_edge("R20", "R21", 1)

    map_graph.add_edge("R21", "R15", 1)
    map_graph.add_edge("R21", "G6", 1)

    map_graph.add_edge("G6", "R16", 1)
    map_graph.add_edge("G6", "R15", 1)
    map_graph.add_edge("G6", "R11", 1)

    map_graph.add_edge("R16", "R11", 1)
    map_graph.add_edge("R16", "R7", 1)

    map_graph.add_edge("R7", "E2", 1)

    map_graph.add_edge("G2", "E2", 1)
    map_graph.add_edge("G2", "R11", 1)
    map_graph.add_edge("G2", "R3", 1)
    map_graph.add_edge("G2", "R6", 1)

    map_graph.add_edge("R3", "R5", 1)
    map_graph.add_edge("R3", "R6", 1)

    map_graph.add_edge("R5", "E1", 1)
    map_graph.add_edge("R5", "G3", 1)
    map_graph.add_edge("R5", "R6", 1)

    map_graph.add_edge("R6", "E1", 1)
    map_graph.add_edge("R6", "G3", 1)
    map_graph.add_edge("R6", "R15", 1)
    map_graph.add_edge("R6", "R11", 1)
    map_graph.add_edge("R6", "E2", 1)

    map_graph.add_edge("G3", "E1", 1)
    map_graph.add_edge("G3", "R10", 1)

    map_graph.add_edge("E1", "R8", 1)
    map_graph.add_edge("E1", "R9", 1)
    map_graph.add_edge("E1", "R14", 1)
    map_graph.add_edge("E1", "R10", 1)

    map_graph.add_edge("R11", "E2", 1)
    map_graph.add_edge("R11", "R10", 1)
    map_graph.add_edge("R11", "R15", 1)

    map_graph.add_edge("R10", "R8", 1)
    map_graph.add_edge("R10", "R9", 1)
    map_graph.add_edge("R10", "R14", 1)
    map_graph.add_edge("R10", "R15", 1)

    map_graph.add_edge("R15", "R9", 1)
    map_graph.add_edge("R15", "R14", 1)
    map_graph.add_edge("R15", "R19", 1)

    map_graph.add_edge("R14", "R19", 1)
    map_graph.add_edge("R14", "G5", 1)
    map_graph.add_edge("R14", "R13", 1)
    map_graph.add_edge("R14", "R9", 1)

    map_graph.add_edge("R9", "G5", 1)
    map_graph.add_edge("R9", "R13", 1)
    map_graph.add_edge("R9", "R8", 1)

    map_graph.add_edge("G5", "R13", 1)
    map_graph.add_edge("G5", "R19", 1)

    map_graph.add_edge("R13", "R8", 1)
    map_graph.add_edge("R13", "R19", 1)

    # ---------- Teste rápido ----------
    # print("Nós criados (primeiros 10):")
    # for p in map_graph.places[:10]:
    #     print(f"ID: {p.get_id():2d}  |  Nome: {p.get_name()}")

    # print("\nGrafo (primeiras linhas):")
    # print(map_graph)

    # print("\nTodas as arestas:")
    # print(map_graph.imprime_aresta())

    # testar bfs
    origem = "R3"
    destino = "G5"
    
    print(f"\n--- A testar BFS de {origem} para {destino} ---")
    
    caminho_resultado = bfs(map_graph, origem, destino)
    
    if caminho_resultado:
        print("✅ Sucesso! Caminho encontrado:")
        print(caminho_resultado)
    else:
        print("❌ Caminho não encontrado.")
    # -------------

if __name__ == "__main__":
    main()