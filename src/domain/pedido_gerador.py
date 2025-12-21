import random
import datetime
import time
from src.domain.structs import Pedido, PrioridadePedido, EstadoPedido

def gerar_pedido_aleatorio(localizacoes: list[str], id_pedido: int) -> Pedido:
    """Gera um Pedido com valores aleatórios."""
    p = Pedido(
        id=id_pedido,
        localizacao_origem=random.choice(localizacoes),
        localizacao_destino=random.choice(localizacoes),
        numero_passageiros=random.randint(1, 4),
        horario_pretendido=f"{random.randint(0,23)}:{random.randint(0,59)}", #!!! Horario em String
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
        