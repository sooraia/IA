# map.py
from .place import Place, PlaceType
from src.utils import distancia_euclidiana, distancia_manhattan

class Map:
    def __init__(self):
        self.places = []
        self.graph = {}                     # key = objeto Place, valor = lista de tuplos (vizinho, custo)
        self.pontos_recolha = []
        self.postos_abastecimento = []
        self.postos_carregamento = []

    def __str__(self):
        out = ""
        for node, neighbours in self.graph.items():
            out += f"{node}: {neighbours}\n"
        return out

    def get_place(self, name: str) -> Place | None:
        for p in self.places:
            if p.get_name() == name:
                return p
        return None

    def imprime_aresta(self):
        s = ""
        for node, lista in self.graph.items():
            for vizinho in lista:
                s += f"{node} -> {vizinho}\n"
        return s

    def get_nodes(self):
        return self.places

    def get_street_distance(self, node1: Place, node2: Place):
        return distancia_manhattan(node1, node2)

    def calc_total_distance(self, caminho):
        total = 0
        for i in range(len(caminho)-1):
            total += self.get_street_distance(caminho[i], caminho[i+1])
        return total

    def get_neighbours(self, place: Place):
        return self.graph.get(place, [])

    def add_edge(self, name1: str, name2: str):
        p1 = self.get_place(name1)
        p2 = self.get_place(name2)
        if p1 is None or p2 is None:
            print(f"Aviso: nó não encontrado -> {name1}-{name2}")
            return

        # store neighbour without explicit cost (cost will be computed when needed)
        self.graph[p1].append(p2)
        self.graph[p2].append(p1)   # grafo não-direcionado

    def add_place(self, place_type: PlaceType, coord):
        new_place = Place(place_type, coord)
        seq = 0
        lista = []

        # calcular número sequencial (começa em 1)
        if place_type == PlaceType.RECOLHA_DE_PASSAGEIROS:
            seq = len(self.pontos_recolha) + 1
            lista = self.pontos_recolha
        elif place_type == PlaceType.POSTO_DE_ABASTECIMENTO:
            seq = len(self.postos_abastecimento) + 1
            lista = self.postos_abastecimento
        elif place_type == PlaceType.ESTACAO_DE_CARGA:
            seq = len(self.postos_carregamento) + 1
            lista = self.postos_carregamento

        new_place.generate_name(seq)
        new_place.set_id(len(self.places) + 1)   # ID começa em 1

        self.places.append(new_place)
        lista.append(new_place)
        self.graph[new_place] = []               # inicializa lista de vizinhos

    def posto_mais_proximo(self, origem: str, tipo: PlaceType) -> Place:
        local_origem = self.get_place(origem)
        estacoes = []
        if tipo == PlaceType.POSTO_DE_ABASTECIMENTO:
            estacoes = self.postos_abastecimento
        elif tipo == PlaceType.ESTACAO_DE_CARGA:
            estacoes = self.postos_carregamento

        posto_mais_prox = None
        distancia_minima = float('inf')

        for estacao in estacoes:
            if estacao.current_veiculos +1 <= estacao.max_veiculos:
                distancia = distancia_euclidiana(local_origem.get_id(), estacao.get_id())
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    posto_mais_prox = estacao

        return posto_mais_prox