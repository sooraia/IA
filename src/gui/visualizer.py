import pygame
import math
from graph.map import Map
from graph.place import PlaceType
from domain.structs import EstadoVeiculo, TipoVeiculo
from utils import horaSimuladaAtual

LARGURA_ECRA = 800
ALTURA_ECRA = 800

COR_FUNDO = (255, 255, 255)
RAIO_NO = 15
COR_RECOLHA = (150, 180, 250)
COR_ABASTECIMENTO = (160, 230, 160)
COR_CARREGAMENTO = (255, 210, 140)
COR_PADRAO = (200, 200, 200)
COR_TEXTO = (0, 0, 0)
LARGURA_ESTRADA = 8
COR_CARRO = (100, 255, 100)
COR_CARRO_OCUPADO = (255, 100, 100)
TAMANHO_CARRO = 12


class Visualizer:
    def __init__(self, map_graph: Map, estado=None):
        pygame.init()
        self.screen = pygame.display.set_mode((LARGURA_ECRA, ALTURA_ECRA))
        self.estado = estado
        pygame.display.set_caption("TaxiGreen - Interface Gráfica")
        self.clock = pygame.time.Clock()
        self.map_graph = map_graph
        self.font = pygame.font.SysFont('Arial', 12)
        self.scale_x = LARGURA_ECRA / 10.0
        self.scale_y = ALTURA_ECRA / 10.0
        self.previous_positions = {}
        self.car_img = None
        self.car_ev_img = None
        self.bg_img = None
        
        car_path = 'gui/car.png'
        car_ev_path = 'gui/carEV.png'
        map_path = 'gui/map.jpeg'

        if (car_path):
            raw_car = pygame.image.load(car_path)
            self.car_img = pygame.transform.scale(raw_car, (40, 20))
        
        if (car_ev_path):
            raw_car_ev = pygame.image.load(car_ev_path)
            self.car_ev_img = pygame.transform.scale(raw_car_ev, (40, 20))
        
        if (map_path):
            self.bg_img = pygame.image.load(map_path)
            self.bg_img = pygame.transform.scale(self.bg_img, (LARGURA_ECRA, ALTURA_ECRA))

    def transform_coord(self, coord):
        x, y = coord
        screen_x = (x * self.scale_x) + 50
        screen_y = ALTURA_ECRA - (y * self.scale_y) - 50
        return (screen_x, screen_y)

    def draw_edges(self):
        drawn_edges = set()
        
        for node, edges in self.map_graph.graph.items():
            for (neighbor, tipo_zona, cruzamentos) in edges:
                pair = tuple(sorted((node.get_name(), neighbor.get_name())))
                if pair in drawn_edges:
                    continue
                
                drawn_edges.add(pair)
                
                if tipo_zona == "Old town":
                    cor_estrada = (180, 140, 90)
                elif tipo_zona == "Residencial":
                    cor_estrada = (90, 160, 130)
                else:
                    cor_estrada = (130, 140, 160)
                
                pontos = [node.coord]
                if cruzamentos:
                    pontos.extend(cruzamentos)
                pontos.append(neighbor.coord)
                
                for i in range(len(pontos) - 1):
                    start_pos = self.transform_coord(pontos[i])
                    end_pos = self.transform_coord(pontos[i + 1])
                    pygame.draw.line(self.screen, cor_estrada, start_pos, end_pos, LARGURA_ESTRADA)

    def draw_traffic(self):
        drawn_edges = set()
        hora_atual = horaSimuladaAtual()
        traffic_surface = pygame.Surface((LARGURA_ECRA, ALTURA_ECRA), pygame.SRCALPHA)
        
        for node, edges in self.map_graph.graph.items():
            for (neighbor, tipo_zona, cruzamentos) in edges:
                pair = tuple(sorted((node.get_name(), neighbor.get_name())))
                if pair in drawn_edges:
                    continue
                
                drawn_edges.add(pair)
                fator_transito = self.map_graph.get_fator_transito(tipo_zona, hora_atual)
                
                if fator_transito <= 1.1:
                    cor_transito = (0, 180, 0, 50)
                elif fator_transito <= 1.3:
                    cor_transito = (255, 150, 0, 65)
                else:
                    cor_transito = (255, 50, 50, 80)
                
                pontos = [node.coord]
                if cruzamentos:
                    pontos.extend(cruzamentos)
                pontos.append(neighbor.coord)
                
                for i in range(len(pontos) - 1):
                    start_pos = self.transform_coord(pontos[i])
                    end_pos = self.transform_coord(pontos[i + 1])
                    pygame.draw.line(traffic_surface, cor_transito, start_pos, end_pos, 4)
        
        self.screen.blit(traffic_surface, (0, 0))

    def draw_nodes(self):
        for node in self.map_graph.places:
            pos = self.transform_coord(node.coord)
            color = COR_PADRAO
            if node.placeType == PlaceType.RECOLHA_DE_PASSAGEIROS:
                color = COR_RECOLHA
            elif node.placeType == PlaceType.POSTO_DE_ABASTECIMENTO:
                color = COR_ABASTECIMENTO
            elif node.placeType == PlaceType.ESTACAO_DE_CARGA:
                color = COR_CARREGAMENTO
            
            pygame.draw.circle(self.screen, color, (int(pos[0]), int(pos[1])), RAIO_NO)
            pygame.draw.circle(self.screen, (0,0,0), (int(pos[0]), int(pos[1])), RAIO_NO, 1)
            
            text_surf = self.font.render(node.get_name(), True, COR_TEXTO)
            text_rect = text_surf.get_rect(center=(int(pos[0]), int(pos[1])))
            self.screen.blit(text_surf, text_rect)

    def draw_vehicles(self):
        if not self.estado:
            return
            
        for veiculo in self.estado.veiculos:
            pos = veiculo.posicao
            screen_pos = self.transform_coord(pos)
            
            color = COR_CARRO
            if veiculo.estado == EstadoVeiculo.OCUPADO:
                color = COR_CARRO_OCUPADO
            elif veiculo.estado == EstadoVeiculo.ABASTECER:
                color = (0, 0, 255)
            
            car_image = None
            if veiculo.tipo == TipoVeiculo.ELETRICO and self.car_ev_img:
                car_image = self.car_ev_img
            elif self.car_img:
                car_image = self.car_img
            
            if car_image:
                prev_pos = self.previous_positions.get(veiculo.id)
                if prev_pos:
                    dx = screen_pos[0] - prev_pos[0]
                    dy = screen_pos[1] - prev_pos[1]
                    if abs(dx) > 0.5 or abs(dy) > 0.5:
                        angle = math.degrees(math.atan2(-dy, dx)) + 180
                        self.previous_positions[veiculo.id + '_angle'] = angle
                
                angle = self.previous_positions.get(veiculo.id + '_angle', 0)
                self.previous_positions[veiculo.id] = screen_pos
                
                rotated_car = pygame.transform.rotate(car_image, angle)
                dest_rect = rotated_car.get_rect(center=(int(screen_pos[0]), int(screen_pos[1])))
                self.screen.blit(rotated_car, dest_rect)
                
                pygame.draw.circle(self.screen, color, (int(screen_pos[0]) + 15, int(screen_pos[1]) - 10), 4)
            else:
                pygame.draw.circle(self.screen, color, (int(screen_pos[0]), int(screen_pos[1])), TAMANHO_CARRO)
                pygame.draw.circle(self.screen, (0,0,0), (int(screen_pos[0]), int(screen_pos[1])), TAMANHO_CARRO, 1)
            
            id_surf = self.font.render(veiculo.id.split('-')[1], True, (0,0,0))
            self.screen.blit(id_surf, (int(screen_pos[0])-5, int(screen_pos[1])-20))

    def run(self, nome_algoritmo=""):
        running = True
        print(f"Interface iniciada.")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if self.bg_img:
                self.screen.blit(self.bg_img, (0, 0))
            else:
                self.screen.fill(COR_FUNDO)
            
            self.draw_edges()
            self.draw_traffic()
            self.draw_nodes()
            self.draw_vehicles()
            
            if self.estado:
                algo_text = f"Algoritmo: {nome_algoritmo}"
                algo_surf = self.font.render(algo_text, True, (0, 0, 0))
                pygame.draw.rect(self.screen, (255, 255, 255, 200), (5, 5, algo_surf.get_width() + 10, 25))
                self.screen.blit(algo_surf, (10, 10))
                
                status_text = f"Pedidos: {self.estado.pedidos_completados}/{self.estado.max_pedidos}"
                status_surf = self.font.render(status_text, True, (0, 0, 0))
                pygame.draw.rect(self.screen, (255, 255, 255, 200), (5, 30, status_surf.get_width() + 10, 25))
                self.screen.blit(status_surf, (10, 35))
                
                hora_sim = horaSimuladaAtual()
                hora_text = hora_sim.strftime("%H:%M")
                hora_font = pygame.font.SysFont('Arial', 24, bold=True)
                hora_surf = hora_font.render(hora_text, True, (0, 0, 0))
                hora_x = LARGURA_ECRA - hora_surf.get_width() - 15
                pygame.draw.rect(self.screen, (255, 255, 255, 220), (hora_x - 5, 5, hora_surf.get_width() + 10, 30))
                self.screen.blit(hora_surf, (hora_x, 8))

            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()