
import datetime
from time import time


hora_real_inicial = 0

def distancia_manhattan(place1, place2):
    return abs(place1.coord[0] - place2.coord[0]) + abs(place1.coord[1] - place2.coord[1])

def distancia_euclidiana(place1, place2):
    return ((place1.coord[0] - place2.coord[0])**2 + (place1.coord[1] - place2.coord[1])**2) ** (1/2)

def set_hora_real_inicial(hora):
    global hora_real_inicial
    hora_real_inicial = hora

def horaSimuladaAtual():
        dif = datetime.now() - hora_real_inicial
        dif = dif.total_seconds()

        dif_sim = dif * 144 # 10 min * 144 = 1440 min = 24h
        
        delta_sim = datetime.timedelta(seconds=dif_sim)
        hora_sim = 5 + delta_sim # 5 -> hora simulada em que o sistema começa
        
        return hora_sim
