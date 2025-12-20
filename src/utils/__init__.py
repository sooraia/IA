
def distancia_manhattan(place1, place2):
    return abs(place1.coord[0] - place2.coord[0]) + abs(place1.coord[1] - place2.coord[1])

def distancia_euclidiana(place1, place2):
    return ((place1.coord[0] - place2.coord[0])**2 + (place1.coord[1] - place2.coord[1])**2) ** (1/2)