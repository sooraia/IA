import json
import os
import random
import datetime
import time
from src.domain.structs import Pedido, PrioridadePedido, EstadoPedido
from utils import horaSimuladaAtual

def gerar_pedido_aleatorio(localizacoes: list[str], id_pedido: int) -> Pedido:
    """Gera um Pedido com valores aleatórios."""

    origem = random.choice(localizacoes)
    localizacoesDestino = localizacoes.copy()
    localizacoesDestino.remove(origem)
    destino = random.choice(localizacoesDestino)
    p = Pedido(
        id=id_pedido,
        localizacao_origem=origem,
        localizacao_destino=destino,
        numero_passageiros=random.randint(1, 4),
        tempo_maximo_espera=datetime.timedelta(minutes=random.randint(5, 30)),
        horario_pretendido=horaSimuladaAtual() + datetime.timedelta(minutes=random.randint(0, 60)),
        prioridade=random.choice(list(PrioridadePedido)),
        preferencia_ambiental=random.choice([True, False])
    )
    return p;

# Numa thread
def gerar_pedidos(localizacoes: list[str], quantidade: int):
    """Generator que produz pedidos a cada N segundos."""
    id_pedido = 0
    while id_pedido < quantidade:
        intervalo = random.randint(1,3)
        p = gerar_pedido_aleatorio(localizacoes, id_pedido)
        yield p  # Devolve pedido e pausa
        id_pedido += 1
        time.sleep(intervalo)  # Dorme N segundos entre pedidos


def load_pedidos():
    pedidos = []
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, 'data', 'pedidos.json')
    with open(file_path, 'r') as f:
        pedidos_data = json.load(f)
        for p_data in pedidos_data["pedidos"]:
            pedido = Pedido(
                id=p_data['id'],
                localizacao_origem=p_data['localizacao_origem'],
                localizacao_destino=p_data['localizacao_destino'],
                numero_passageiros=p_data['numero_passageiros'],
                horario_pretendido=datetime.datetime.combine(horaSimuladaAtual().date(),
                                                            datetime.datetime.strptime(p_data['horario_pretendido'], '%H:%M:%S').time()),
                tempo_maximo_espera=datetime.timedelta(minutes=p_data['tempo_maximo_espera_minutos']),
                prioridade=p_data['prioridade'],
                preferencia_ambiental=p_data['preferencia_ambiental']
            )
            pedidos.append(pedido)
    return pedidos

def gerar_pedidos_data():
    """Generator que produz pedidos com base em informações fornecidas."""
    pedidos = load_pedidos()
    pedidos.sort(key=lambda p: p.horario_pretendido)
    for p in pedidos:
        if p.horario_pretendido - datetime.timedelta(minutes=30) > horaSimuladaAtual(): # esperar até o horário pretendido
            intervalo = (p.horario_pretendido - datetime.timedelta(minutes=30) - horaSimuladaAtual()).total_seconds()
            time.sleep(intervalo/144)
        yield p

        