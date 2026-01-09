from src.utils import distancia_manhattan
from src.domain import velocidade_media

# Custo entre dois Places usando a distância de Manhattan (das ruas)
def distance_heuristic(start, end, vehicle):
    return distancia_manhattan(start, end)

# Custo entre dois Places usando o tempo estimado (distância / velocidade)
def time_heuristic(start, end, vehicle):
    distance = distancia_manhattan(start, end)
    return distance / velocidade_media

def combined_heuristic(start, end, vehicle):
    distance_cost = distance_heuristic(start, end, vehicle)
    time_cost = time_heuristic(start, end, vehicle)
    return distance_cost + 10*time_cost
