from dataclasses import dataclass, field
import threading
from typing import List, Dict, Optional
from src.domain.pedido_gerador import gerar_pedidos
from src.domain.structs import Veiculo, Pedido, TipoVeiculo, EstadoVeiculo, EstadoPedido, velocidade_media
from src.utils import distancia_manhattan, distancia_euclidiana
from threading import Thread
from graph.map import Map
from graph.place import Place, PlaceType
import json

@dataclass
class Estado:
    veiculos: List[Veiculo]
    pedidos: List[Pedido]
    pedidos_lock: threading.Lock
    mapa: Map
    # Métricas acumuladas para cálculo do custo
    custo_operacional_acumulado: float = 0.0
    tempo_espera_total: float = 0.0
    emissoes_totais: float = 0.0
    distancia_vazio_total: float = 0.0
    pedidos_rejeitados: int = 0

    max_pedidos = 30
    pedidos_completados = 0
    pedidos_gerados = 0
    
    def __init__ (self, mapa: Map):
        self.veiculos = []
        self.pedidos = []
        self.mapa = mapa
        self.custo_operacional_acumulado = 0.0
        self.tempo_espera_total = 0.0
        self.emissoes_totais = 0.0
        self.distancia_vazio_total = 0.0
        self.pedidos_rejeitados = 0
        self.pedidos_lock = threading.Lock()
        self.load_veiculos()

    def load_veiculos(self):
        with open('data/veiculos.json', 'r') as f:
            veiculos_data = json.load(f)
            for v_data in veiculos_data["veiculos"]:
                veiculo = Veiculo(
                    id=v_data['id'],
                    tipo=TipoVeiculo(v_data['tipo']),
                    autonomia_max=v_data['autonomia_max'],
                    autonomia_atual=v_data['autonomia_atual'],
                    capacidade_passageiros=v_data['capacidade_passageiros'],
                    tempo_recarga_abastecimento=v_data['tempo_recarga_abastecimento'],
                    localizacao=v_data['localizacao'],
                    estado=EstadoVeiculo(v_data['estado']),
                    custo_por_km=v_data['custo_por_km'],
                    posicao=tuple(v_data['posicao']),
                    emissoes_por_km=v_data['emissoes_por_km']
                )
                self.veiculos.append(veiculo)

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
    
    def posto_mais_proximo(self, tipo_veiculo: TipoVeiculo, localizacao_atual: str) -> Place:
        if tipo_veiculo == TipoVeiculo.ELETRICO:
            posto = self.mapa.posto_mais_proximo(localizacao_atual, PlaceType.ESTACAO_DE_CARGA)
        else:
            posto = self.mapa.posto_mais_proximo(localizacao_atual, PlaceType.POSTO_DE_ABASTECIMENTO)
        return posto

    def get_veiculos_possiveis(self, pedido: Pedido, veiculos_disponiveis: List[Veiculo]) -> List[Veiculo]:
        veiculos_possiveis = []
        for veiculo in veiculos_disponiveis:
            distancia_min = distancia_euclidiana(self.mapa.get_place(veiculo.localizacao),self.mapa.get_place(pedido.localizacao_origem)) 
            + distancia_euclidiana(self.mapa.get_place(pedido.localizacao_origem),self.mapa.get_place(pedido.localizacao_destino)) # limite inferior oara a distancia
            if veiculo.pode_atender_pedido(
                pedido.numero_passageiros,
                distancia= distancia_min,
                preferencia_ambiental=pedido.preferencia_ambiental
            ):
                veiculos_possiveis.append(veiculo)
        return veiculos_possiveis

    def heuristica_atribuicao_pedidos(self, veiculo, pedido):
        dist = distancia_euclidiana(self.mapa.get_place(veiculo.localizacao), self.mapa.get_place(pedido.localizacao_origem)) 
        + distancia_euclidiana(self.mapa.get_place(pedido.localizacao_origem), self.mapa.get_place(pedido.localizacao_destino))

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
                self.pedidos_completados+=1

        pedidos_pendentes.sort(key= lambda p: p.tempo_ate_timeout())  # ordenar por tempo até timeout (< primeiro)
        pedidos_pendentes.sort(key= lambda p:p.prioridade_valor(), reverse=True)  # ordenar por prioridade (> primeiro)

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
                            autonomia_reserva = distancia_manhattan(self.mapa.get_place(pedido.localizacao_destino), posto)
                            if (r1.distance + r2.distance + autonomia_reserva) <= veiculo.autonomia_atual:
                                veiculos_disponiveis.remove(veiculo)
                                self.atualizar_custos(veiculo, passageiros=False, distancia_percorrida= r1.distance)
                                self.atualizar_custos(veiculo, passageiros=True, distancia_percorrida= r2.distance)
                                Thread(target=veiculo.atender_pedido, args=(r1.path, r2.path, pedido,)).start()
                                self.pedidos_completados+=1
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
            
    def adicionar_pedido(self, pedido: Pedido):
        with self.pedidos_lock:
            self.pedidos.append(pedido)
            self.pedidos_gerados+=1
            
    def thread_produtora_pedidos(self, localizacoes, quantidade):
        generator = gerar_pedidos(localizacoes, quantidade)
        
        for novo_pedido in generator:
            self.adicionar_pedido(novo_pedido)


    def run(self, algoritmo_procura):
        self.pedidos_done = False
        nomes_locais = [place.get_name() for place in self.mapa.places]
        thread_gera_pedidos = threading.Thread(
            target = self.thread_produtora_pedidos, 
            args=(nomes_locais, self.max_pedidos),
            daemon=True
        )
        thread_gera_pedidos.start()

        while self.pedidos_completados != self.max_pedidos:
            self.atualizar_estado(algoritmo_procura)
                
            

    
                    

