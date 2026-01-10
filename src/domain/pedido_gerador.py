import json
import random
import datetime
import time
from domain.structs import Pedido, PrioridadePedido
from utils import horaSimuladaAtual

def gerar_pedido_aleatorio(localizacoes: list[str], id_pedido: int, horario_limite=None) -> Pedido:
    """
    Gera um Pedido com valores aleatórios.
    
    Args:
        localizacoes: Lista de localizações possíveis
        id_pedido: ID do pedido
        janela_temporal: Janela temporal em minutos onde o horário pretendido pode cair (padrão: 60 minutos)
    """
    origem = random.choice(localizacoes)
    localizacoesDestino = localizacoes.copy()
    localizacoesDestino.remove(origem)
    destino = random.choice(localizacoesDestino)
    horario_max = horaSimuladaAtual() + datetime.timedelta(minutes=random.randint(0, 30))
    if horario_limite and horario_max > horario_limite:
        horario_max = horario_limite
    p = Pedido(
        id=id_pedido,
        localizacao_origem=origem,
        localizacao_destino=destino,
        numero_passageiros=random.randint(1, 4),
        tempo_maximo_espera=datetime.timedelta(minutes=random.randint(5, 30)),
        horario_pretendido=horario_max,
        prioridade=random.choice(list(PrioridadePedido)),
        preferencia_ambiental=random.choice([True, False])
    )
    return p

# Numa thread
def gerar_pedidos(localizacoes: list[str], quantidade: int, janela_temporal: int = 240):
    """
    Generator que produz pedidos distribuídos ao longo da janela temporal.
    
    Args:
        localizacoes: Lista de localizações possíveis
        quantidade: Número de pedidos a gerar
        janela_temporal: Janela temporal em minutos onde os pedidos devem chegar (padrão: 60 minutos)
    """
    horario_inicial = horaSimuladaAtual()
    horario_limite = horario_inicial + datetime.timedelta(minutes=janela_temporal)
    id_pedido = 0
    # Converter janela temporal para segundos e dividir pela quantidade de pedidos
    intervalo_medio = (janela_temporal * 60) / quantidade if quantidade > 0 else 60
    intervalo_medio_real = intervalo_medio / 144
    
    while id_pedido < quantidade:
        # Variação aleatória em torno do intervalo médio (±30%)
        intervalo = random.uniform(intervalo_medio * 0.7, intervalo_medio * 1.3)
        p = gerar_pedido_aleatorio(localizacoes, id_pedido, horario_limite)
        yield p  # Devolve pedido e pausa
        id_pedido += 1
        time.sleep(intervalo_medio_real)  # Dorme N segundos entre pedidos



def load_pedidos():
    pedidos = []
    with open('data/pedidos.json', 'r') as f:
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

        