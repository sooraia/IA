
def distancia_manhattan(place1, place2):
    return abs(place1.x - place2.x) + abs(place1.y - place2.y)

def distancia_euclidiana(place1, place2):
    return ((place1.x - place2.x)**2 + (place1.y - place2.y)**2) ** (1/2)