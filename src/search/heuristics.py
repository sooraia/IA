from src.utils import distancia_manhattan

# Custo entre dois Places usando a distância de Manhattan (das ruas)
def distance_heuristic(start, end, vehicle):
    return distancia_manhattan(start, end)

# Custo entre dois Places usando o tempo estimado (distância / velocidade)
def time_heuristic(start, end, vehicle):
    if vehicle.speed == 0:
        return float('inf')
    distance = distancia_manhattan(start, end)
    return distance / vehicle.speed

def combined_heuristic(start, end, vehicle):
    distance_cost = distance_heuristic(start, end, vehicle)
    time_cost = time_heuristic(start, end, vehicle)
    return distance_cost + time_cost
