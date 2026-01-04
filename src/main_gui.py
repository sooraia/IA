import sys
import os
import datetime
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import set_hora_real_inicial
from domain.state import Estado
from search.BFS import bfs_search
from search.DFS import dfs_search
from search.UCS import ucs_search
from search.AStar import a_star_search
from search.heuristics import time_heuristic
from search.iterative import iterative
from search.Greedy import greedy_search
from main import build_map
from gui.visualizer import Visualizer


def selecionar_algoritmo():
    algoritmos = {
        '1': (bfs_search, 'BFS (Pesquisa em Largura)'),
        '2': (dfs_search, 'DFS (Pesquisa em Profundidade)'),
        '3': (ucs_search, 'UCS (Pesquisa de Custo Uniforme)'),
        '4': (a_star_search, 'A* (A-Estrela)'),
        '5': (greedy_search, 'Greedy (Pesquisa Gulosa)'),
        '6': (iterative, 'Iterative Deepening (Aprofundamento Iterativo)'),
    }
    
    print("\n" + "=" * 60)
    print("        SELECIONAR ALGORITMO DE PROCURA")
    print("=" * 60)
    print("  [1] BFS  - Pesquisa em Largura")
    print("  [2] DFS  - Pesquisa em Profundidade")
    print("  [3] UCS  - Pesquisa de Custo Uniforme")
    print("  [4] A*   - A-Estrela")
    print("  [5] Greedy - Pesquisa Gulosa")
    print("  [6] Iterative Deepening - Aprofundamento Iterativo")
    print("=" * 60)
    
    while True:
        escolha = input("\nEscolha o algoritmo [1-6] (ou 'q' para sair): ").strip().lower()
        
        if escolha == 'q':
            print("A sair...")
            sys.exit(0)
        
        if escolha in algoritmos:
            func, nome = algoritmos[escolha]
            print(f"\n Algoritmo selecionado: {nome}")
            return func, nome
        else:
            print("Opção inválida. Por favor, escolha entre 1 e 6.")


def main():
    map_graph_instance = build_map()
    set_hora_real_inicial(datetime.datetime.now())
    estado = Estado(map_graph_instance)
    algoritmo_func, nome_algoritmo = selecionar_algoritmo()
    
    print("\n" + "=" * 60)
    print("SIMULAÇÃO INICIADA (modo gráfico)")
    print("=" * 60)
    print(f"Algoritmo: {nome_algoritmo}")
    print("=" * 60 + "\n")

    try:
        viz = Visualizer(map_graph_instance, estado)

        sim_thread = threading.Thread(target=estado.run, args=(algoritmo_func, time_heuristic))
        sim_thread.daemon = True
        sim_thread.start()
        
        viz.run(nome_algoritmo)
        
    except ImportError as e:
        print(f"Não foi possível importar o Visualizer: {e}")
        print("Certifique-se de que tem o pygame instalado")
    except Exception as e:
        print(f"Ocorreu um erro durante a visualização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
