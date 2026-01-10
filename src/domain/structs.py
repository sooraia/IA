from dataclasses import dataclass
import datetime
import time
from enum import Enum

from graph.place import Place
from utils import horaSimuladaAtual, distancia_euclidiana
from domain import velocidade_media

class TipoVeiculo(Enum):
    ELETRICO = "eletrico"
    COMBUSTAO = "combustao"

class EstadoVeiculo(Enum):
    DISPONIVEL = "disponivel"
    OCUPADO = "ocupado"
    ABASTECER = "abastecer"

class PrioridadePedido(Enum):
    NORMAL = "normal"
    PREMIUM = "premium"
    URGENTE = "urgente"

class EstadoPedido(Enum):
    PENDENTE = "pendente"
    ATRIBUIDO = "atribuido"
    EM_TRANSPORTE = "em_transporte"
    CONCLUIDO = "concluido"
    REJEITADO = "rejeitado"


@dataclass
class Veiculo:
    id: str # matricula
    tipo: TipoVeiculo
    autonomia_max: float
    autonomia_atual: float
    capacidade_passageiros: int
    tempo_recarga_abastecimento: int
    localizacao: str # nome do nó do grafo
    estado: EstadoVeiculo
    custo_por_km: float
    posicao: tuple[float, float]
    emissoes_por_km: float
    
    tempo_viagem: datetime.timedelta

    def __init__(self, id: str, tipo: TipoVeiculo, autonomia_max: float, autonomia_atual: float, capacidade_passageiros: int, estado: EstadoVeiculo,
                 tempo_recarga_abastecimento: int, localizacao: str, custo_por_km: float, emissoes_por_km: float, posicao: tuple[float, float]=(0.0, 0.0)):
        self.id = id
        self.tipo = tipo
        self.autonomia_max = autonomia_max
        self.autonomia_atual = autonomia_atual
        self.capacidade_passageiros = capacidade_passageiros
        self.tempo_recarga_abastecimento = tempo_recarga_abastecimento
        self.localizacao = localizacao
        self.estado = estado
        self.custo_por_km = custo_por_km
        self.emissoes_por_km = emissoes_por_km
        self.posicao = posicao
        self.tempo_viagem = datetime.timedelta(0)

    def pode_atender_pedido(self, numero_passageiros: int, distancia: float, preferencia_ambiental: bool) -> bool:
        return (self.estado == EstadoVeiculo.DISPONIVEL and
                self.capacidade_passageiros >= numero_passageiros and
                self.autonomia_atual >= distancia and
                (preferencia_ambiental == True and self.tipo == TipoVeiculo.ELETRICO) or
                 preferencia_ambiental == False)
        
    def calcular_custo_viagem(self, distancia: float) -> float:
        return distancia * self.custo_por_km
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def go_to_position(self, new_position: tuple[float, float], velocidade: float):
        travel_distance = distancia_euclidiana(self.posicao[0], self.posicao[1], new_position[0], new_position[1])
        distancia_percorrida = 0
    
        tempo_viagem_segundos = travel_distance / (velocidade / 3600)
        self.tempo_viagem += datetime.timedelta(seconds=tempo_viagem_segundos)

        tick_rate = 0.05
        distancia_por_tick = velocidade * (144 / 3600) * tick_rate

        while distancia_percorrida < travel_distance:
            distancia_percorrida += distancia_por_tick
            if distancia_percorrida > travel_distance:
                distancia_percorrida = travel_distance
            
            progresso = distancia_percorrida / travel_distance
            self.posicao = (self.posicao[0] + (new_position[0] - self.posicao[0]) * progresso,
                            self.posicao[1] + (new_position[1] - self.posicao[1]) * progresso)
            
            time.sleep(tick_rate)
        self.autonomia_atual -= travel_distance
        self.posicao = new_position
    
    def go_to_location(self, mapa, new_location: Place):
        if self.localizacao == new_location.name:
            return
        (tipo_zona, cruzamentos) = mapa.get_aresta(self.localizacao, new_location.name)
        velocidade = velocidade_media / mapa.get_fator_transito(tipo_zona, horaSimuladaAtual())
        
        for cruzamento in cruzamentos:
            self.go_to_position(cruzamento, velocidade)
        self.go_to_position(new_location.coord, velocidade)
        
        self.localizacao = new_location.name
        

    def atender_pedido(self, mapa, path_origem, path_destino, pedido):
        print(f"Veículo {self.id} a atender pedido {pedido.id} de {pedido.localizacao_origem} para {pedido.localizacao_destino}, estado: {self.estado}")
        print(f"Localizações a percorrer: {[loc.name for loc in path_origem + path_destino]}") 
        print("\n")
        autonomia_inicio = self.autonomia_atual

        # atualiza o tempo de espera se a atribuicao for depois do horario pretendido
        if pedido.horario_pretendido < horaSimuladaAtual():
            pedido.tempo_espera = horaSimuladaAtual() - pedido.horario_pretendido

        #desloca-se para a origem
        path_origem.pop(0)
        for localizacao in path_origem:
            self.go_to_location(mapa, localizacao)

        # espera ate ao horario pretendido e atualiza o tempo de espera
        if pedido.horario_pretendido > horaSimuladaAtual():
            wait_time = (pedido.horario_pretendido - horaSimuladaAtual()).total_seconds() / 144
            time.sleep(wait_time)
            pedido.tempo_espera = datetime.timedelta(0)

        #desloca-se para o destino
        path_destino.pop(0)
        pedido.estado = EstadoPedido.EM_TRANSPORTE
        for localizacao in path_destino:
            self.go_to_location(mapa, localizacao)

        pedido.estado = EstadoPedido.CONCLUIDO
        self.estado = EstadoVeiculo.DISPONIVEL
        print(f"Veículo {self.id} concluiu pedido {pedido.id}. Gastou {autonomia_inicio - self.autonomia_atual:.2f} de autonomia.")
        print("\n")

    def abastecer(self, mapa, path):
        print(f"Veículo {self.id} a abastecer/carregar")
        print(f"Localizações a percorrer: {[loc.name for loc in path]}. autonomia atual: {self.autonomia_atual:.2f}/ {self.autonomia_max:.2f}")
        print("\n")
        path.pop(0)
        for localizacao in path:
            self.go_to_location(mapa, localizacao)

        tempo_simulado_carregamento = (self.tempo_recarga_abastecimento * (self.autonomia_max - self.autonomia_atual) / self.autonomia_max) * 3600
        tempo_real_carregamento = tempo_simulado_carregamento / 144

        while tempo_real_carregamento > 0:
            self.autonomia_atual += self.autonomia_max / tempo_real_carregamento
            if self.autonomia_atual > self.autonomia_max:
                self.autonomia_atual = self.autonomia_max
                break
            tempo_real_carregamento -= 1
            time.sleep(1)
        print(f"Veículo {self.id} terminou de abastecer/carregar, autonomia atual: {self.autonomia_atual:.2f}/ {self.autonomia_max:.2f}")
        print("\n")
        self.estado = EstadoVeiculo.DISPONIVEL

@dataclass
class Pedido:
    id: str
    localizacao_origem: str
    localizacao_destino: str
    numero_passageiros: int
    horario_pretendido: datetime
    tempo_maximo_espera: datetime.timedelta
    prioridade: PrioridadePedido
    preferencia_ambiental: bool # false para indiferente, true para eletrico
    estado: EstadoPedido
    tempo_espera: datetime.timedelta

    def __init__ (self, id: str, localizacao_origem: str, localizacao_destino: str, numero_passageiros: int,
                  horario_pretendido: datetime, tempo_maximo_espera: datetime.timedelta,
                  prioridade: PrioridadePedido, preferencia_ambiental: bool):
        self.id = id
        self.localizacao_origem = localizacao_origem
        self.localizacao_destino = localizacao_destino
        self.numero_passageiros = numero_passageiros
        self.horario_pretendido = horario_pretendido
        self.tempo_maximo_espera = tempo_maximo_espera
        self.prioridade = prioridade
        self.preferencia_ambiental = preferencia_ambiental
        self.estado = EstadoPedido.PENDENTE
        self.tempo_espera = datetime.timedelta(0)

    def __hash__(self) -> int:
        return hash(self.id)

    def prioridade_valor(self) -> int:
        if self.prioridade == PrioridadePedido.NORMAL:
            return 1
        elif self.prioridade == PrioridadePedido.PREMIUM:
            return 2
        elif self.prioridade == PrioridadePedido.URGENTE:
            return 3
        return 0
    
    def verificar_tempo_rejeicao(self) -> bool:
        if self.horario_pretendido + self.tempo_maximo_espera < horaSimuladaAtual():
            self.estado = EstadoPedido.REJEITADO
            self.tempo_espera = horaSimuladaAtual() - self.horario_pretendido
            return True
        return False
    
    def tempo_ate_timeout(self) -> datetime.timedelta:
        horario_timeout = self.horario_pretendido + self.tempo_maximo_espera
        return horario_timeout - horaSimuladaAtual()

    
    