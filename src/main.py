import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import time
import datetime
from utils import set_hora_real_inicial
from domain.state import Estado

from graph.map import Map
from graph.place import Place, PlaceType
from search.BFS import bfs_search
from search.DFS import dfs_search
from search.UCS import ucs_search



def build_map():
    map_graph = Map()
    N_PONTOS_RECOLHA = 21
    N_POSTOS_ABASTECIMENTO = 6
    N_POSTOS_CARREGAMENTO = 3
    
    pontos_de_recolha_coords = [(4.7, 8.45), (1.8, 7.5), (6.15, 7.85), (0.0, 5.55), (3.85, 6.65), 
                                (6.1, 6.2), (8.65, 6.2), (1.7, 4.5), (2.55, 3.75), (4.75, 4.5),
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

    return map_graph


if __name__ == "__main__":

    map_graph_instance = build_map()
    set_hora_real_inicial(datetime.datetime.now())
    estado = Estado(map_graph_instance)
    estado.run(ucs_search)
    # try:
    #     from gui.visualizer import Visualizer
    #     viz = Visualizer(map_graph_instance)
        
    #     algorithms = {
    #         'UCS': ucs_search
    #     }
        
    #     # Pode alterar o início/fim padrão aqui ou na UI
    # #     viz.run(algorithms, start_node="R1", end_node="R21")
        
    # except ImportError as e:
    #     print(f"Não foi possível importar o Visualizer: {e}")
    #     print("Certifique-se de que está a executar a partir da raiz do projeto ou que 'src' está no python path.")
    # except Exception as e:
    #     print(f"Ocorreu um erro durante a visualização: {e}")

