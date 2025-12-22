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
        intervalo = random.randint(1,10)
        p = gerar_pedido_aleatorio(localizacoes, id_pedido)
        yield p  # Devolve pedido e pausa
        id_pedido += 1
        time.sleep(intervalo)  # Dorme N segundos entre pedidos

        