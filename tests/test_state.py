import unittest
from datetime import datetime
from src.structs import Veiculo, Pedido, TipoVeiculo, EstadoVeiculo, EstadoPedido, PrioridadePedido
from src.taxigreen.domain.state import Estado

class TestEstado(unittest.TestCase):
    def test_estado_initialization(self):
        v1 = Veiculo(
            id="V1",
            tipo=TipoVeiculo.ELETRICO,
            autonomia_max=100.0,
            autonomia_atual=100.0,
            capacidade_passageiros=4,
            tempo_recarga_abastecimento=60,
            localizacao="G3",
            estado=EstadoVeiculo.DISPONIVEL,
            custo_por_km=1.0
        )
        
        p1 = Pedido(
            id="P1",
            localizacao_origem="A",
            localizacao_destino="B",
            numero_passageiros=2,
            horario_pretendido=datetime.now(),
            prioridade=PrioridadePedido.NORMAL,
            preferencia_ambiental=False,
            estado=EstadoPedido.PENDENTE
        )
        
        estado = Estado(
            tempo_atual=0,
            veiculos=[v1],
            pedidos=[p1]
        )
        
        self.assertEqual(estado.tempo_atual, 0)
        self.assertEqual(len(estado.veiculos), 1)
        self.assertEqual(len(estado.pedidos), 1)
        self.assertEqual(estado.custo_operacional_acumulado, 0.0)

    def test_calcular_custo(self):
        estado = Estado(
            tempo_atual=10,
            veiculos=[],
            pedidos=[],
            custo_operacional_acumulado=100.0,
            tempo_espera_total=50.0,
            emissoes_totais=20.0,
            distancia_vazio_total=10.0,
            pedidos_rejeitados=2
        )
        
        pesos = {
            'alpha': 1.0, # custo op
            'beta': 0.5,  # tempo espera
            'gamma': 2.0, # emissoes
            'delta': 0.1, # dist vazio
            'lambda': 10.0 # rejeitados
        }
        
        # C = 1*100 + 0.5*50 + 2*20 + 0.1*10 + 10*2
        # C = 100 + 25 + 40 + 1 + 20 = 186
        
        custo = estado.calcular_custo(pesos)
        self.assertEqual(custo, 186.0)

if __name__ == '__main__':
    unittest.main()
