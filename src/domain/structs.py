from dataclasses import dataclass
import datetime
import time
from enum import Enum

from src.graph.place import Place
from src.utils import horaSimuladaAtual, distancia_euclidiana_to_place

velocidade_media = 40  # km/h

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
    tempo_recarga_abastecimento: int # nao esta no enunciado
    localizacao: str # no do grafo
    estado: EstadoVeiculo
    custo_por_km: float
    posicao: tuple[float, float]
    emissoes_por_km: float

    def pode_atender_pedido(self, numero_passageiros: int, distancia: float, preferencia_ambiental: bool) -> bool:
        return (self.estado == EstadoVeiculo.DISPONIVEL and
                self.capacidade_passageiros >= numero_passageiros and
                self.autonomia_atual >= distancia and
                (preferencia_ambiental == True and self.tipo == TipoVeiculo.ELETRICO) or
                 preferencia_ambiental == False)
    
    def calcular_consumo_viagem(self, distancia: float) -> float:
        if self.tipo == TipoVeiculo.ELETRICO:
            return distancia * 0.2  # kWh
        else:
            return distancia * 0.07  # litros
        
    def calcular_custo_viagem(self, distancia: float) -> float:
        return distancia * self.custo_por_km
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def go_to_location(self, new_location: Place):
        travel_distance = distancia_euclidiana_to_place(self.posicao[0], self.posicao[1], new_location)
        new_position = new_location.coord
        distancia_percorrida = 0

        distancia_por_segundo_real = velocidade_media * (144 / 3600)

        while distancia_percorrida < travel_distance:
            distancia_percorrida += distancia_por_segundo_real
            if distancia_percorrida > travel_distance:
                distancia_percorrida = travel_distance
            
            consumo = self.calcular_consumo_viagem(distancia_por_segundo_real)
            self.autonomia_atual -= consumo
            
            progresso = distancia_percorrida / travel_distance
            self.posicao = (self.posicao[0] + (new_position[0] - self.posicao[0]) * progresso,
                            self.posicao[1] + (new_position[1] - self.posicao[1]) * progresso)
            time.sleep(1)
        
        self.localizacao = new_location.name
        self.posicao = new_position
        

    def atender_pedido(self, path_origem, path_destino, pedido):
        pedido.estado = EstadoPedido.ATRIBUIDO
        print(f"Veículo {self.id} a atender pedido {pedido.id} de {pedido.localizacao_origem} para {pedido.localizacao_destino}")

        # atualiza o tempo de espera se a atribuicao for depois do horario pretendido
        if pedido.horario_pretendido < horaSimuladaAtual():
            pedido.tempo_espera = horaSimuladaAtual() - pedido.horario_pretendido
        print("...")
        #desloca-se para a origem
        self.estado = EstadoVeiculo.OCUPADO

        for localizacao in path_origem:
            self.go_to_location(localizacao)

        # espera ate ao horario pretendido e atualiza o tempo de espera
        if pedido.horario_pretendido > horaSimuladaAtual():
            wait_time = (pedido.horario_pretendido - horaSimuladaAtual()).total_seconds() / 144
            time.sleep(wait_time)
            pedido.tempo_espera = 0

        #desloca-se para o destino
        pedido.estado = EstadoPedido.EM_TRANSPORTE
        for localizacao in path_destino:
            self.go_to_location(localizacao)
        pedido.estado = EstadoPedido.CONCLUIDO
        self.estado = EstadoVeiculo.DISPONIVEL
        print(f"Veículo {self.id} concluiu pedido {pedido.id}")

    def abastecer(self, path):
        self.estado = EstadoVeiculo.ABASTECER
        for localizacao in path:
            self.go_to_location(localizacao)

        tempo_total_carregamento = self.tempo_recarga_abastecimento * (self.autonomia_max - self.autonomia_atual) / self.autonomia_max
        
        while self.autonomia_atual < self.autonomia_max:
            self.autonomia_atual += self.autonomia_max / self.tempo_recarga_abastecimento
            tempo_total_carregamento -= 1
            time.sleep(1)

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

    
    