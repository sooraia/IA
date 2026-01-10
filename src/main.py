import sys
import datetime

from utils import set_hora_real_inicial
from domain.state import Estado
from graph.map import Map
from graph.place import PlaceType
from search.iterative import iterative
from search.BFS import bfs_search
from search.DFS import dfs_search
from search.UCS import ucs_search
from search.AStar import a_star_search
from search.heuristics import time_heuristic
from search.iterative import iterative
from search.Greedy import greedy_search

def build_map():
    map_graph = Map()
    N_PONTOS_RECOLHA = 21
    N_POSTOS_ABASTECIMENTO = 6
    N_POSTOS_CARREGAMENTO = 3
    
    # Coordenadas dos pontos de recolha de passageiros
    pontos_de_recolha_coords = [(4.7, 8.45), (1.8, 7.5), (6.15, 7.85), (0.0, 5.55), (3.85, 6.65), 
                                (6.1, 6.2), (8.65, 6.2), (1.7, 4.5), (2.55, 3.75), (4.75, 4.5),
                                (7.65, 4.8), (0.0, 1.8), (1.3, 2.5), (3.8,2.7), (6.0, 3.0), 
                                (8.6, 3.85), (2.1, 0.0), (3.25, 0.65), (4.14, 1.4), (5.15, 0.1), 
                                (6.8, 1.55)]
    
    # Coordenadas dos postos de abastecimento (combustível)
    postos_de_abastecimento_coords = [(3.2, 8.45), (7.65, 7.6), (4.75,5.6), (0, 4.5), (2.1, 1.8), (7.65, 2.8)]
    
    # Coordenadas das estações de carregamento (elétrico)
    postos_de_carregamento_coords = [(3.2, 6.15), (8.1, 6.2), (4.9, 0.6)]
    
    # Adicionar nós ao grafo do mapa
    # Pontos de recolha de passageiros
    for i in range(N_PONTOS_RECOLHA):
        map_graph.add_place(PlaceType.RECOLHA_DE_PASSAGEIROS, pontos_de_recolha_coords[i])

    # Postos de abastecimento
    for i in range(N_POSTOS_ABASTECIMENTO):
        map_graph.add_place(PlaceType.POSTO_DE_ABASTECIMENTO, postos_de_abastecimento_coords[i])

    # Estações de carregamento
    for i in range(N_POSTOS_CARREGAMENTO):
        map_graph.add_place(PlaceType.ESTACAO_DE_CARGA, postos_de_carregamento_coords[i])

    # Adicionar arestas (ligações) ao grafo do mapa
    map_graph.add_edge("R1", "G1", "Normal", [])
    map_graph.add_edge("R1", "R3", "Residencial", [(4.7, 7.85)])
    map_graph.add_edge("R1", "R5", "Normal", [(4.7, 6.65)])
    map_graph.add_edge("R1", "G3", "Residencial", [])

    map_graph.add_edge("G1", "R2", "Normal", [(1.8, 8.45), (1.45, 8.2), (1.5, 7.8)])
    map_graph.add_edge("G1", "R4", "Normal", [(1.8, 8.45), (1.45, 8.2), (1.05, 8.05), (0.25, 7.4), (0.1, 6.8), (0.05, 6.7)])
    map_graph.add_edge("G1", "E1", "Normal", [])
    map_graph.add_edge("G1", "R5", "Normal", [(3.2, 6.65)])

    map_graph.add_edge("R2", "R4", "Normal", [(1.5, 7.8), (1.45, 8.2), (1.05, 8.05), (0.25, 7.4), (0.1, 6.8), (0.05, 6.7)])
    map_graph.add_edge("R2", "R8", "Normal", [(2.65, 6.65), (1.3, 5.55), (1.7, 5.30)])
    map_graph.add_edge("R2", "E1", "Normal", [(3.1, 6.15)])
    map_graph.add_edge("R2", "R5", "Normal", [(2.65, 6.65)])

    map_graph.add_edge("R4", "R5", "Normal", [(1.3, 5.55), (2.65, 6.65)])
    map_graph.add_edge("R4", "E1", "Normal", [(1.3, 5.55), (2.65, 6.65), (3.1, 6.15)])
    map_graph.add_edge("R4", "R8", "Normal", [(1.3, 5.55), (1.7, 5.30)])
    map_graph.add_edge("R4", "G4", "Normal", [])

    map_graph.add_edge("G4", "R8", "Normal", [])
    map_graph.add_edge("G4", "R13", "Normal", [(1.3, 4.5)])
    map_graph.add_edge("G4", "R12", "Normal", [])

    map_graph.add_edge("R12", "R13", "Normal", [(1.3, 1.8)])
    map_graph.add_edge("R12", "G5", "Normal", [])

    map_graph.add_edge("R17", "R18", "Normal", [(2.35, 0)])
    map_graph.add_edge("R17", "G5", "Normal", [])

    map_graph.add_edge("R18", "G5", "Normal", [(2.55, 1.8)])
    map_graph.add_edge("R18", "R9", "Normal", [(2.55, 1.8)])
    map_graph.add_edge("R18", "R19", "Old town", [])

    map_graph.add_edge("E3", "R19", "Old town", [])
    map_graph.add_edge("E3", "R15", "Old town", [(4.39, 1.1), (5.4, 1.75), (5.65, 2.35), (6.0, 2.8)])
    map_graph.add_edge("E3", "R20", "Old town", [])

    map_graph.add_edge("R20", "R21", "Old town", [(6.55, 0.95)])

    map_graph.add_edge("R21", "R15", "Old town", [(5.65, 2.35), (6.0, 2.8)])
    map_graph.add_edge("R21", "G6", "Old town", [(7.15, 2.2)])

    map_graph.add_edge("G6", "R16", "Old town", [(8.1, 3.2), (8.7, 3.45)])
    map_graph.add_edge("G6", "R15", "Old town", [(7.55, 3)])
    map_graph.add_edge("G6", "R11", "Old town", [(7.65, 3.1)])

    map_graph.add_edge("R16", "R11", "Old town", [(8.6, 4.8)])
    map_graph.add_edge("R16", "R7", "Old town", [])

    map_graph.add_edge("R7", "E2", "Residencial", [])

    map_graph.add_edge("G2", "E2", "Residencial", [(7.65, 6.2)])
    map_graph.add_edge("G2", "R11", "Residencial", [])
    map_graph.add_edge("G2", "R3", "Residencial", [(6.15, 7.6)])
    map_graph.add_edge("G2", "R6", "Residencial", [(6.15, 7.6)])

    map_graph.add_edge("R3", "R5", "Residencial", [(4.7, 7.85), (4.7, 6.65)])
    map_graph.add_edge("R3", "R6", "Residencial", [])

    map_graph.add_edge("R5", "E1", "Normal", [(3.2, 6.65), (2.65, 6.65), (3.1,6.15)])
    map_graph.add_edge("R5", "G3", "Residencial", [(4.75, 6.65)])
    map_graph.add_edge("R5", "R6", "Residencial", [(4.75, 6.65), (4.75, 6.2)])

    map_graph.add_edge("R6", "E1", "Residencial", [])
    map_graph.add_edge("R6", "G3", "Residencial", [(4.75, 6.2)])
    map_graph.add_edge("R6", "R15", "Residencial", [(6.05, 4.5)])
    map_graph.add_edge("R6", "R11", "Residencial", [(7.65, 6.2)])
    map_graph.add_edge("R6", "E2", "Residencial", [])

    map_graph.add_edge("G3", "E1", "Residencial", [(4.75, 6.2)])
    map_graph.add_edge("G3", "R10", "Residencial", [])

    map_graph.add_edge("E1", "R8", "Normal", [(3.1, 6.15), (2.65, 6.65), (1.3, 5.55), (1.7,5.30)])
    map_graph.add_edge("E1", "R9", "Normal", [(3.1, 6.15), (3.65, 5.3), (2.45, 4.9), (2.55, 4.5)])
    map_graph.add_edge("E1", "R14", "Old town", [(3.1, 6.15), (3.65, 5.3), (3.8, 4.8)])
    map_graph.add_edge("E1", "R10", "Residencial", [(3.1, 6.15), (3.65, 5.3), (3.8, 4.8), (3.8, 4.5)])

    map_graph.add_edge("R11", "E2", "Residencial", [(7.65, 6.2)])
    map_graph.add_edge("R11", "R10", "Residencial", [(7.1, 4.8), (6.05, 4.5)])
    map_graph.add_edge("R11", "R15", "Old town", [(7.65, 3.1), (7.55, 3.0)])

    map_graph.add_edge("R10", "R8", "Residencial", [])
    map_graph.add_edge("R10", "R9", "Residencial", [(2.55, 4.5)])
    map_graph.add_edge("R10", "R14", "Residencial", [(3.8, 4.5)])
    map_graph.add_edge("R10", "R15", "Residencial", [(6.05, 4.5)])

    map_graph.add_edge("R15", "R9", "Old town", [(5.2, 3.45), (3.8, 3.45), (3.8, 3.75)])
    map_graph.add_edge("R15", "R14", "Old town", [(5.2, 3.45), ((3.8, 3.45))])
    map_graph.add_edge("R15", "R19", "Old town", [(6.0, 2.8), (5.65, 2.35), (5.4, 1.75), (4.39, 1.1)])

    map_graph.add_edge("R14", "R19", "Old town", [(3.9, 2.0)])
    map_graph.add_edge("R14", "G5", "Old town", [(3.9, 2.0), (2.55, 1.8)])
    map_graph.add_edge("R14", "R13", "Old town", [(3.8, 2.5)])
    map_graph.add_edge("R14", "R9", "Old town", [(3.8, 3.75)])

    map_graph.add_edge("R9", "G5", "Normal", [(2.55, 1.8)])
    map_graph.add_edge("R9", "R13", "Normal", [(2.55, 2.5)])
    map_graph.add_edge("R9", "R8", "Normal", [(2.55, 4.5)])

    map_graph.add_edge("G5", "R13", "Normal", [(1.3, 1.8)])
    map_graph.add_edge("G5", "R19", "Old town", [(2.55, 1.8), (3.9, 2.0)])

    map_graph.add_edge("R13", "R8", "Normal", [(1.3, 4.5)])
    map_graph.add_edge("R13", "R19", "Old town", [(3.8, 2.5), (3.9, 2.0)])

    return map_graph


def selecionar_algoritmo():
    algoritmos = {
        '1': (bfs_search, 'BFS (Procura em Largura)'),
        '2': (dfs_search, 'DFS (Procura em Profundidade)'),
        '3': (ucs_search, 'UCS (Procura de Custo Uniforme)'),
        '4': (a_star_search, 'A* (A-Estrela)'),
        '5': (greedy_search, 'Greedy (Procura Gulosa)'),
        '6': (iterative, 'Iterative (Aprofundamento Iterativo)'),
    }
    
    print("\n" + "==================================================")
    print("        SELECIONAR ALGORITMO DE PROCURA")
    print("==================================================")
    print("  [1] BFS  - Procura em Largura")
    print("  [2] DFS  - Procura em Profundidade")
    print("  [3] UCS  - Procura de Custo Uniforme")
    print("  [4] A*   - A-Estrela")
    print("  [5] Greedy - Procura Gulosa")
    print("  [6] Iterative - Aprofundamento Iterativo")
    print("==================================================")
    
    while True:
        escolha = input("\nEscolha o algoritmo [1-6] (ou 'q' para sair): ").strip().lower()
        
        if escolha == 'q':
            print("A sair...")
            sys.exit(0)
        
        if escolha in algoritmos:
            func, nome = algoritmos[escolha]
            print(f"\n✓ Algoritmo selecionado: {nome}")
            return func, nome
        else:
            print("Opção inválida. Por favor, escolha entre 1 e 6.")


def main():
    map_graph_instance = build_map()
    set_hora_real_inicial(datetime.datetime.now())
    estado = Estado(map_graph_instance)
    algoritmo, nome_algoritmo = selecionar_algoritmo()
    
    print("\n" + "=" * 60)
    print("SIMULAÇÃO INICIADA (modo consola)")
    print("=" * 60)
    print(f"Algoritmo: {nome_algoritmo}")
    print("=" * 60 + "\n")

    estado.run(algoritmo, time_heuristic)
    
    print("\n" + "=" * 60)
    print("MÉTRICAS FINAIS:")
    print("=" * 60)
    custo_total = estado.get_custo_total()
    custo_procura = estado.get_custo_procura()
    print(f"Custo Total (soma): {custo_total:.2f}")
    print("=" * 60)

if __name__ == "__main__":
    main()