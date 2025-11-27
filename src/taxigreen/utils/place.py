# place.py
from enum import Enum

class PlaceType(Enum):
    RECOLHA_DE_PASSAGEIROS = "R"
    POSTO_DE_ABASTECIMENTO = "G"
    ESTACAO_DE_CARGA = "E"

class Place:
    def __init__(self, placeType):
        self.placeType = placeType
        self.name = ""
        self.id = -1

    def __str__(self):
        return f"node {self.name}"

    def __repr__(self):
        return f"node {self.name}"

    def set_id(self, new_id):          # agora atribui diretamente
        self.id = new_id

    def generate_name(self, number):
        self.name = self.placeType.value + str(number)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Place):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)