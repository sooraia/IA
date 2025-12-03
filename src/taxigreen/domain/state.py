from dataclasses import dataclass, field
from typing import List, Dict, Optional
from src.structs import Veiculo, Pedido, TipoVeiculo, EstadoVeiculo, EstadoPedido

@dataclass
class Estado:
    tempo_atual: float
    veiculos: List[Veiculo]
    pedidos: List[Pedido]
    
    # Métricas acumuladas para cálculo do custo
    custo_operacional_acumulado: float = 0.0
    tempo_espera_total: float = 0.0
    emissoes_totais: float = 0.0
    distancia_vazio_total: float = 0.0
    pedidos_rejeitados: int = 0
    
    def __hash__(self) -> int:
        # Hash baseada em tempo, veículos e pedidos
        return hash((
            self.tempo_atual,
            tuple(self.veiculos),
            tuple(self.pedidos)
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Estado):
            return NotImplemented
        return (self.tempo_atual == other.tempo_atual and
                self.veiculos == other.veiculos and
                self.pedidos == other.pedidos)

    def calcular_custo(self, pesos: Dict[str, float]) -> float:
        """
        Calcula o custo total da solução com base nos pesos fornecidos.
        C = α*O + β*T + γ*E + δ*D + λ*PR
        
        pesos deve conter chaves: 'alpha', 'beta', 'gamma', 'delta', 'lambda'
        """
        alpha = pesos.get('alpha', 0.0)
        beta = pesos.get('beta', 0.0)
        gamma = pesos.get('gamma', 0.0)
        delta = pesos.get('delta', 0.0)
        lam = pesos.get('lambda', 0.0)
        
        return (alpha * self.custo_operacional_acumulado +
                beta * self.tempo_espera_total +
                gamma * self.emissoes_totais +
                delta * self.distancia_vazio_total +
                lam * self.pedidos_rejeitados)

    def clone(self) -> 'Estado':
        import copy
        return copy.deepcopy(self)
