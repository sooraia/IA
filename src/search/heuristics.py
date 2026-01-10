from utils import distancia_manhattan
from domain import velocidade_media

# Custo entre dois Places usando a distância de Manhattan (das ruas)
def distance_heuristic(start, end):
    return distancia_manhattan(start, end)

# Custo entre dois Places usando o tempo estimado (distância / velocidade)
def time_heuristic(start, end):
    distance = distancia_manhattan(start, end)
    return distance / velocidade_media
