from dataclasses import dataclass
import datetime
from enum import Enum

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


@dataclass
class Pedido:
    id: str
    localizacao_origem: str
    localizacao_destino: str
    numero_passageiros: int
    horario_pretendido: datetime
    prioridade: PrioridadePedido
    preferencia_ambiental: bool # false para indiferente, true para eletrico
    estado: EstadoPedido

    def __hash__(self) -> int:
        return hash(self.id)


    
    