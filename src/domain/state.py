from dataclasses import dataclass
import threading
from time import sleep
from typing import List, Dict, Optional
from src.domain.pedido_gerador import gerar_pedidos, gerar_pedidos_data
from src.domain.structs import Veiculo, Pedido, TipoVeiculo, EstadoVeiculo, EstadoPedido, velocidade_media
from src.search import SearchResult
from src.utils import distancia_manhattan, distancia_euclidiana
from threading import Thread
from graph.map import Map
from graph.place import Place, PlaceType
import json
import os

@dataclass
class Estado:
    veiculos: List[Veiculo]
    pedidos: List[Pedido]
    pedidos_lock: threading.Lock
    mapa: Map

    # Métricas para o custo total
    custo_operacional_acumulado: float = 0.0
    tempo_espera_total: float = 0.0
    emissoes_totais: float = 0.0
    distancia_vazio_total: float = 0.0
    pedidos_rejeitados: int = 0

    # Métricas para comparação dos algoritmos de procura
    nos_visitados: int = 0
    nos_caminho: int = 0
    tempo_procura: float = 0.0
    tempo_viagem_total: float = 0.0

    max_pedidos = 100
    pedidos_completados = 0
    pedidos_gerados = 0
    distancia_total = 0.0
    running = False
    
    def __init__ (self, mapa: Map):
        self.mapa = mapa
        self.pedidos_lock = threading.Lock()
        self.reset()
    
    def reset(self):
        self.veiculos = []
        self.pedidos = []
        self.custo_operacional_acumulado = 0.0
        self.tempo_espera_total = 0.0
        self.emissoes_totais = 0.0
        self.distancia_vazio_total = 0.0
        self.pedidos_rejeitados = 0
        self.distancia_total = 0.0
        self.pedidos_completados = 0
        self.pedidos_gerados = 0
        self.running = False
        self.load_veiculos()

    def load_veiculos(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, 'data', 'veiculos.json')
        with open(file_path, 'r') as f:
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
            distancia_min = (distancia_euclidiana(self.mapa.get_place(veiculo.localizacao).coord[0], 
                                                 self.mapa.get_place(veiculo.localizacao).coord[1], 
                                                 self.mapa.get_place(pedido.localizacao_origem).coord[0],
                                                 self.mapa.get_place(pedido.localizacao_origem).coord[1])
                            + distancia_euclidiana(self.mapa.get_place(pedido.localizacao_origem).coord[0],
                                                self.mapa.get_place(pedido.localizacao_origem).coord[1],
                                                self.mapa.get_place(pedido.localizacao_destino).coord[0],
                                                self.mapa.get_place(pedido.localizacao_destino).coord[1])) # limite inferior para a distancia
            if veiculo.pode_atender_pedido(
                pedido.numero_passageiros,
                distancia= distancia_min,
                preferencia_ambiental=pedido.preferencia_ambiental
            ):
                veiculos_possiveis.append(veiculo)
        return veiculos_possiveis

    def heuristica_atribuicao_pedidos(self, veiculo, pedido):
        dist = (distancia_euclidiana(self.mapa.get_place(veiculo.localizacao).coord[0],
                                    self.mapa.get_place(veiculo.localizacao).coord[1],
                                    self.mapa.get_place(pedido.localizacao_origem).coord[0],
                                    self.mapa.get_place(pedido.localizacao_origem).coord[1])
             + distancia_euclidiana(self.mapa.get_place(pedido.localizacao_origem).coord[0], 
                                    self.mapa.get_place(pedido.localizacao_origem).coord[1], 
                                    self.mapa.get_place(pedido.localizacao_destino).coord[0],
                                    self.mapa.get_place(pedido.localizacao_destino).coord[1]))

        ambiental = 1
        if veiculo.tipo == TipoVeiculo.ELETRICO:
            ambiental = 0

        tempo_estimado = dist / velocidade_media #horas
        return (
            1.0 * dist +
            2.0 * tempo_estimado +
            5.0 * ambiental
        )

    def atualizar_custos(self, veiculo: Veiculo, passageiros: bool, resultados: SearchResult):
        distancia_percorrida = resultados.distance
        self.custo_operacional_acumulado +=  veiculo.calcular_custo_viagem(distancia_percorrida)
        self.emissoes_totais += distancia_percorrida * veiculo.emissoes_por_km
        self.distancia_total += distancia_percorrida
        
        if not passageiros:
            self.distancia_vazio_total += distancia_percorrida

        self.nos_visitados += resultados.visited
        self.nos_caminho += len(resultados.path)
        self.tempo_procura += resultados.time_taken


    # Função principal para atualizar o estado do sistema: atribuição de pedidos e gestão dos veículos
    # O argumento algoritmo_procura é uma o algoritmo escolhido para implementar a procura da melhor rota no grafo
    def atualizar_estado(self, algoritmo_procura, heuristica): 
        pedidos_pendentes = [p for p in self.pedidos if p.estado == EstadoPedido.PENDENTE]
        veiculos_disponiveis = [v for v in self.veiculos if v.estado == EstadoVeiculo.DISPONIVEL]

        for p in pedidos_pendentes:
            if p.verificar_tempo_rejeicao():
                print("pedido rejeitado: " + str(p.id))
                self.pedidos_rejeitados += 1
                self.pedidos_completados+=1
                
        pedidos_pendentes = [p for p in pedidos_pendentes if p.estado != EstadoPedido.REJEITADO]

        pedidos_pendentes.sort(key= lambda p: p.tempo_ate_timeout())  # ordenar por tempo até timeout (< primeiro)
        pedidos_pendentes.sort(key= lambda p:p.prioridade_valor(), reverse=True)  # ordenar por prioridade (> primeiro)

        # Atribuir pedidos
        if len(pedidos_pendentes) > 0:
            for pedido in pedidos_pendentes:
                veiculos_possiveis = self.get_veiculos_possiveis(pedido, veiculos_disponiveis)

                if len(veiculos_possiveis) > 0:
                    veiculos_possiveis.sort(key = lambda v: self.heuristica_atribuicao_pedidos(v, pedido))

                    for veiculo in veiculos_possiveis:
                        r1 = algoritmo_procura(self.mapa, veiculo.localizacao, pedido.localizacao_destino, veiculo, heuristica) # rota local atual -> local origem pedido
                        r2 = algoritmo_procura(self.mapa, pedido.localizacao_destino, pedido.localizacao_origem, veiculo, heuristica) # rota local origem pedido -> local destino pedido

                        if r1 is not None and r2 is not None:
                            # autonomia de reserva estimada necessaria para deslocação para estacao de recarga após atendimento do pedido
                            posto = self.posto_mais_proximo(veiculo.tipo, pedido.localizacao_origem)
                            autonomia_reserva = distancia_manhattan(self.mapa.get_place(pedido.localizacao_destino), posto)
                            if (r1.distance + r2.distance + autonomia_reserva) <= veiculo.autonomia_atual:
                                veiculos_disponiveis.remove(veiculo)
                                self.atualizar_custos(veiculo, passageiros=False, resultados= r1)
                                self.atualizar_custos(veiculo, passageiros=True, resultados= r2)
                                veiculo.estado = EstadoVeiculo.OCUPADO
                                pedido.estado = EstadoPedido.ATRIBUIDO
                                Thread(target=veiculo.atender_pedido, args=(self.mapa, r1.path, r2.path, pedido,)).start()
                                self.pedidos_completados+=1
                                break
        
        # Verificar necessidade de recarga/abastecimento
        for veiculo in self.veiculos:
            if veiculo.estado == EstadoVeiculo.DISPONIVEL:
                if veiculo.autonomia_atual < (0.2* veiculo.autonomia_max):
                    print(f"Veículo {veiculo.id} com autonomia baixa ({veiculo.autonomia_atual:.2f}/{veiculo.autonomia_max:.2f}), a procurar posto de recarga/abastecimento.")
                    print(f"Etsado: {veiculo.estado}")
                    estacao = self.posto_mais_proximo(veiculo.tipo, veiculo.localizacao)
                    print(f"Veículo {veiculo.id} a caminho do posto de recarga/abastecimento em {estacao.name}")
                    results = algoritmo_procura(self.mapa, veiculo.localizacao, estacao.name, veiculo, heuristica)
                    if results.path is None:
                        print(f"Veículo {veiculo.id} não conseguiu encontrar rota para posto de recarga/abastecimento.")
                    if results is not None and results.path is not None:
                        self.atualizar_custos(veiculo, passageiros=False, resultados= results)
                        veiculo.estado = EstadoVeiculo.ABASTECER
                        Thread(target=veiculo.abastecer, args=(self.mapa, results.path,)).start()
    
    def get_custo_total(self) -> float:
        for p in self.pedidos:
            self.tempo_espera_total += p.tempo_espera.total_seconds() / 60.0  # min
        print("custo operacional:" + str(self.custo_operacional_acumulado))
        print("tempo espera:" + str(self.tempo_espera_total) + " minutos")
        print("emissoes totais:" + str(self.emissoes_totais))
        print("distancia vazio total:" + str(self.distancia_vazio_total))
        print("pedidos rejeitados:" + str(self.pedidos_rejeitados))
        print("distancia total:" + str(self.distancia_total))
        return self.custo_operacional_acumulado + self.tempo_espera_total + self.emissoes_totais + self.distancia_vazio_total + self.pedidos_rejeitados
    
    def get_custo_procura(self) -> float:
        for v in self.veiculos:
            self.tempo_viagem_total += v.tempo_viagem.total_seconds() / 60.0 
        print("tempo viagem total:" + str(self.tempo_viagem_total) + " minutos simulados")
        print("nós visitados:" + str(self.nos_visitados))
        print("nós no caminho:" + str(self.nos_caminho))
        print("tempo procura:" + str(self.tempo_procura*1000) + " ms reais")

        res = str(self.tempo_procura*1000) + ", " + str(self.tempo_viagem_total) + ", " + str(self.distancia_total) + ", " + str(self.nos_caminho) + ", " + str(self.nos_visitados)
        with open('resultados_procura.txt', 'a') as f:
            f.write(res + '\n')

        return self.nos_visitados + self.nos_caminho + self.tempo_procura

    def adicionar_pedido(self, pedido: Pedido):
        with self.pedidos_lock:
            self.pedidos.append(pedido)
            self.pedidos_gerados+=1
            
    def thread_produtora_pedidos(self):
        #generator = gerar_pedidos_data()
        generator = gerar_pedidos(
            localizacoes=[place.name for place in self.mapa.places],
            quantidade=self.max_pedidos,
        )
        
        for novo_pedido in generator:
            self.adicionar_pedido(novo_pedido)

    def run(self, algoritmo_procura, heuristica):
        self.running = True
        self.pedidos_done = False
        thread_gera_pedidos = threading.Thread(
            target = self.thread_produtora_pedidos, 
            daemon=True
        )
        thread_gera_pedidos.start()

        while self.pedidos_completados != self.max_pedidos and self.running:
            self.atualizar_estado(algoritmo_procura, heuristica)
            if not self.running: break
            
        print("Simulation loop ended")
        if self.running:
            while any((pedido.estado != EstadoPedido.CONCLUIDO and pedido.estado != EstadoPedido.REJEITADO) for pedido in self.pedidos):
                if not self.running: break
                pass
            self.get_custo_total()
