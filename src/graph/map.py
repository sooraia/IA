from .place import Place, PlaceType
from src.utils import distancia_euclidiana
from datetime import datetime
from src.domain import velocidade_media

class Map:
    def __init__(self):
        self.places = []
        self.graph = {}  
        self.aresta_info = {}
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

    def get_distancia_rota(self, node1: Place, node2: Place):
        neighbours = self.get_neighbours(node1)
        last_node = node1.coord
        distancia = 0
        for (neighbour,_,cruzamentos) in neighbours:
            if neighbour == node2:
                if(len(cruzamentos) > 0):
                    last_node = cruzamentos[0]
                    distancia += distancia_euclidiana(node1.coord[0], node1.coord[1], cruzamentos[0][0], cruzamentos[0][1])
                for i in range(len(cruzamentos)-1):
                    distancia += distancia_euclidiana(cruzamentos[i][0], cruzamentos[i][1], cruzamentos[i + 1][0], cruzamentos[i + 1][1])
                    last_node = cruzamentos[i + 1]
                distancia += distancia_euclidiana(node2.coord[0], node2.coord[1], last_node[0], last_node[1])
                return distancia
        return None

    def calc_total_distance(self, caminho):
        total = 0
        for i in range(len(caminho)-1):
            total += self.get_distancia_rota(caminho[i], caminho[i+1])
        return total
    
    def get_aresta(self, name1: str, name2: str) -> tuple: 
        place1 = self.get_place(name1)
        place2 = self.get_place(name2)
        if place1 is None or place2 is None:
            return None
        neighbours = self.get_neighbours(place1)
        for (neighbour, tipo_zona, cruzamentos) in neighbours:
            if neighbour == place2:
                return (tipo_zona, cruzamentos)
        return None

    def get_neighbours(self, place: Place):
        return self.graph.get(place, [])


    def add_edge(self, name1: str, name2: str, tipo_zona: str, cruzamentos: list = []):
        p1 = self.get_place(name1)
        p2 = self.get_place(name2)
        if p1 is None or p2 is None:
            print(f"Aviso: nó não encontrado -> {name1}-{name2}")
            return
        
        # Inverter a lista de cruzamentos para a direção oposta
        cruzamentos_reverse = list(reversed(cruzamentos))
            
        self.graph[p1].append((p2, tipo_zona, cruzamentos))
        self.graph[p2].append((p1, tipo_zona, cruzamentos_reverse))

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
        new_place.set_id(len(self.places) + 1) # ID começa em 1

        self.places.append(new_place)
        lista.append(new_place)
        self.graph[new_place] = [] # inicializa lista de vizinhos

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
                distancia = distancia_euclidiana(local_origem.coord[0],
                                                 local_origem.coord[0], 
                                                 estacao.coord[0],
                                                 estacao.coord[1])
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    posto_mais_prox = estacao
        return posto_mais_prox
    
    def get_fator_transito(self, tipo_zona: str, hora: datetime) -> float:
        hora_atual = hora.hour + hora.minute / 60.0
        if tipo_zona == "Old town":
            fator_zona = 0.8
        elif tipo_zona == "Residencial":
            fator_zona = 0.2
        else:
            fator_zona = 0.4

        if 0 <= hora_atual < 7:
            fator_hora = 0.0
        elif (7 <= hora_atual < 9.5) or (17 <= hora_atual < 19.5):
            fator_hora = 1.0
        else:
            fator_hora = 0.5
            
        fator_transito = 1.0 + (fator_zona * fator_hora)

        return fator_transito
    
    def get_cost(self, src, dest, tipo_zona: str, hora: datetime):
        distance = self.get_distancia_rota(src, dest)
        transito = self.get_fator_transito(tipo_zona, hora)

        tempo_base = distance / velocidade_media
    
        tempo_com_transito = tempo_base * transito
        
        return tempo_com_transito