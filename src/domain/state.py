from dataclasses import dataclass, field
import threading
from typing import List, Dict, Optional
from src.domain.pedido_gerador import gerar_pedidos
from src.domain.structs import Veiculo, Pedido, TipoVeiculo, EstadoVeiculo, EstadoPedido, velocidade_media
from src.utils import distancia_manhattan, distancia_euclidiana
from threading import Thread
from graph.map import Map
from graph.place import PlaceType
from src.utils import horaSimuladaAtual

@dataclass
class Estado:
    tempo_atual: float
    veiculos: List[Veiculo]
    pedidos: List[Pedido]
    mapa: Map
    
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
    
    def posto_mais_proximo(self, tipo_veiculo: TipoVeiculo, localizacao_atual: str) -> str:
        if tipo_veiculo == TipoVeiculo.ELETRICO:
            posto = self.mapa.posto_mais_proximo(localizacao_atual, PlaceType.ESTACAO_DE_CARGA)
        else:
            posto = self.mapa.posto_mais_proximo(localizacao_atual, PlaceType.POSTO_DE_ABASTECIMENTO)
        return posto.get_name()

    def get_veiculos_possiveis(self, pedido: Pedido, veiculos_disponiveis: List[Veiculo]) -> List[Veiculo]:
        veiculos_possiveis = []
        for veiculo in veiculos_disponiveis:
            distancia_min = distancia_euclidiana(veiculo.localizacao, pedido.localizacao_origem) + distancia_euclidiana(pedido.localizacao_origem, pedido.localizacao_destino) # limite inferior oara a distancia
            if veiculo.pode_atender_pedido(
                pedido.numero_passageiros,
                distancia= distancia_min,
                preferencia_ambiental=pedido.preferencia_ambiental
            ):
                veiculos_possiveis.append(veiculo)
        return veiculos_possiveis

    def heuristica_atribuicao_pedidos(self, veiculo, pedido):
        dist = self.distancia_euclidiana(veiculo.localizacao, pedido.localizacao_origem) + self.distancia_euclidiana(pedido.localizacao_origem, pedido.localizacao_destino)

        ambiental = 1
        if veiculo.tipo == TipoVeiculo.ELETRICO:
            ambiental = 0

        tempo_estimado = dist / velocidade_media #horas
        return (
            1.0 * dist +
            2.0 * tempo_estimado +
            5.0 * ambiental
        )

    def atualizar_custos(self, veiculo: Veiculo, passageiros: bool, distancia_percorrida: float):
        self.custo_operacional_acumulado +=  veiculo.calcular_custo_viagem(distancia_percorrida)
        self.emissoes_totais += distancia_percorrida * veiculo.emissoes_por_km
        
        if not passageiros:
            self.distancia_vazio_total += distancia_percorrida

    # Função principal para atualizar o estado do sistema: atribuição de pedidos e gestão dos veículos
    # O argumento algoritmo_procura é uma o algoritmo escolhido para implementar a procura da melhor rota no grafo
    def atualizar_estado(self, algoritmo_procura): 
        pedidos_pendentes = [p for p in self.pedidos if p.estado == EstadoPedido.PENDENTE]
        veiculos_disponiveis = [v for v in self.veiculos if v.estado == EstadoVeiculo.DISPONIVEL]

        for p in pedidos_pendentes:
            if p.verificar_tempo_rejeicao():
                self.pedidos_rejeitados += 1

        pedidos_pendentes.sort(key= lambda p: p.tempo_ate_timeout())  # ordenar por tempo até timeout (< primeiro)
        pedidos_pendentes.sort(key= lambda p:p.prioriedade_valor(), reverse=True)  # ordenar por prioridade (> primeiro)

        # Atribuir pedidos
        if len(pedidos_pendentes) > 0:
            for pedido in pedidos_pendentes:
                veiculos_possiveis = self.get_veiculos_possiveis(pedido, veiculos_disponiveis)

                if len(veiculos_possiveis) > 0:
                    veiculos_possiveis.sort(key = lambda v: self.heuristica_atribuicao_pedidos(v, pedido))

                    for veiculo in veiculos_possiveis:
                        r1 = algoritmo_procura(self.mapa, veiculo.localizacao, pedido.localizacao_destino) # rota local atual -> local origem pedido
                        r2 = algoritmo_procura(self.mapa, pedido.localizacao_destino, pedido.localizacao_origem) # rota local origem pedido -> local destino pedido

                        if r1 is not None and r2 is not None:
                            # autonomia de reserva estimada necessaria para deslocação para estacao de recarga após atendimento do pedido
                            posto = self.posto_mais_proximo(veiculo.tipo, pedido.localizacao_origem)
                            autonomia_reserva = distancia_manhattan(pedido.localizacao_destino, posto)
                            if (r1.distanca + r2.distancia + autonomia_reserva) <= veiculo.autonomia_atual:
                                veiculos_disponiveis.remove(veiculo)
                                self.atualizar_custos(veiculo, passageiros=False, distancia_percorrida= r1.distancia)
                                self.atualizar_custos(veiculo, passageiros=True, distancia_percorrida= r2.distancia)
                                Thread(target=veiculo.atender_pedido, args=(r1.path, r2.path, pedido,)).start()
                                break
        
        # Verificar necessidade de recarga/abastecimento
        for veiculo in self.veiculos:
            if veiculo.estado == EstadoVeiculo.DISPONIVEL:
                if veiculo.autonomia_atual < (0.2* veiculo.autonomia_max):
                    estacao = self.posto_mais_proximo(veiculo.tipo, veiculo.localizacao)
                    results = algoritmo_procura(self.mapa, veiculo.localizacao, estacao)
                    if results is not None:
                        self.atualizar_custos(veiculo, passageiros=False, distancia_percorrida= results.distancia)
                        Thread(target=veiculo.abastecer(), args=(results.path,)).start()
    
    def get_custo_total(self) -> float:
        for p in self.pedidos:
            self.tempo_espera_total += p.tempo_espera.total_seconds() / 60.0  # min

        return self.custo_operacional_acumulado + self.tempo_espera_total + self.emissoes_totais + self.distancia_vazio_total + self.pedidos_rejeitados
            
    def get_fator_transito(tipo_zona: str, hora_atual: float) -> float:

        if tipo_zona == "Old town":
            fator_zona = 3.0
        elif tipo_zona == "Residencial":
            fator_zona = 1.0
        else:
            fator_zona = 2.0

        if 0 <= hora_atual < 7:
            fator_hora = 0.5
        elif (7 <= hora_atual < 9.5) or (17 <= hora_atual < 19.5):
            fator_hora = 1.5
        else:
            fator_hora = 1.0

        return fator_zona * fator_hora
    
      
    def thread_produtora_pedidos(self, localizacoes, quantidade):
        generator = gerar_pedidos(localizacoes, quantidade)
        
        for novo_pedido in generator:
            # Usar lock para adicionar à lista global com segurança ------------!!!!!!!!!!
            self.adicionar_pedido(novo_pedido)

    def run(self, algoritmo_procura):
        nomes_locais = [place.get_name() for place in self.mapa.places]
        thread_gera_pedidos = threading.Thread(
            target = self.thread_produtora_pedidos, 
            args=(self, nomes_locais, 30),
            daemon=True
        )
        thread_gera_pedidos.start()
        
        while True:
            self.atualizar_estado(algoritmo_procura)
            

    
                    

