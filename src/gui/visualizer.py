import pygame
import sys
from src.graph.map import Map
from src.graph.place import PlaceType

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BG_COLOR = (255, 255, 255)
NODE_RADIUS = 15
FONT_SIZE = 12
COLOR_RECOLHA = (100, 100, 255)
COLOR_ABASTECIMENTO = (100, 255, 100)
COLOR_CARREGAMENTO = (255, 165, 0)
COLOR_DEFAULT = (200, 200, 200)
COLOR_EDGE = (50, 50, 50)
COLOR_TEXT = (0, 0, 0)

# Styles
ROAD_WIDTH = 8
ROAD_COLOR = (100, 100, 100)
PATH_WIDTH = 4
PATH_COLOR = (255, 0, 0) # Red
CAR_COLOR = (255, 255, 0) # Yellow taxi?
CAR_SIZE = 12

class Visualizer:
    def __init__(self, map_graph: Map):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TaxiGreen AI - Visualização da Cidade")
        self.clock = pygame.time.Clock()
        self.map_graph = map_graph
        self.font = pygame.font.SysFont('Arial', FONT_SIZE) # Tentar negrito?
        
        # Determinar escala
        self.scale_x = SCREEN_WIDTH / 10.0 
        self.scale_y = SCREEN_HEIGHT / 10.0
        
        # Margens
        self.margin_x = 50
        self.margin_y = 50
        
        # Recalcular escala com base nas margens reais
        self.draw_width = SCREEN_WIDTH - 2 * self.margin_x
        self.draw_height = SCREEN_HEIGHT - 2 * self.margin_y
        self.scale_x = self.draw_width / 10.0 
        self.scale_y = self.draw_height / 10.0

        # Estado da animação
        self.anim_path = None
        self.anim_index = 0
        self.anim_progress = 0.0
        self.anim_speed = 0.05 # Velocidade da animação (0.0 a 1.0 por segmento)
        self.car_pos = None

    def transform_coord(self, coord):
        x, y = coord
        screen_x = self.margin_x + (x * self.scale_x)
        screen_y = SCREEN_HEIGHT - self.margin_y - (y * self.scale_y)
        return (screen_x, screen_y)

    def draw_edges(self):
        drawn_edges = set()
        
        for node, edges in self.map_graph.graph.items():
            start_pos = self.transform_coord(node.coord)
            for (neighbor, cost, type_zone) in edges:
                pair = tuple(sorted((node.get_name(), neighbor.get_name())))
                if pair in drawn_edges:
                    continue
                
                drawn_edges.add(pair)
                end_pos = self.transform_coord(neighbor.coord)
                
                # Desenhar estrada (linha grossa)
                pygame.draw.line(self.screen, ROAD_COLOR, start_pos, end_pos, ROAD_WIDTH)
                
                # Desenhar custo (opcional)
                # mid_x = (start_pos[0] + end_pos[0]) / 2
                # mid_y = (start_pos[1] + end_pos[1]) / 2
                # text_surf = self.font.render(str(cost), True, (100, 100, 100))
                # self.screen.blit(text_surf, (mid_x, mid_y)) 

    def draw_nodes(self):
        for node in self.map_graph.places:
            pos = self.transform_coord(node.coord)
            
            color = COLOR_DEFAULT
            if node.placeType == PlaceType.RECOLHA_DE_PASSAGEIROS:
                color = COLOR_RECOLHA
            elif node.placeType == PlaceType.POSTO_DE_ABASTECIMENTO:
                color = COLOR_ABASTECIMENTO
            elif node.placeType == PlaceType.ESTACAO_DE_CARGA:
                color = COLOR_CARREGAMENTO
            
            # Desenhar círculo (ponto da cidade)
            pygame.draw.circle(self.screen, color, (int(pos[0]), int(pos[1])), NODE_RADIUS)
            pygame.draw.circle(self.screen, (0,0,0), (int(pos[0]), int(pos[1])), NODE_RADIUS, 1) # Borda
            
            # Desenhar Rótulo
            text_surf = self.font.render(node.get_name(), True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=(int(pos[0]), int(pos[1])))
            self.screen.blit(text_surf, text_rect)

    def draw_path(self, path):
        if not path or len(path) < 2:
            return
            
        for i in range(len(path) - 1):
            start_node = path[i]
            end_node = path[i+1]
            
            start_pos = self.transform_coord(start_node.coord)
            end_pos = self.transform_coord(end_node.coord)
            
            # Linha de percurso (um pouco mais fina que a estrada, mas visível)
            pygame.draw.line(self.screen, PATH_COLOR, start_pos, end_pos, PATH_WIDTH)

    def draw_car(self):
        if self.car_pos:
            x, y = self.car_pos
            # Simular um carro com um retângulo ou círculo
            pygame.draw.circle(self.screen, CAR_COLOR, (int(x), int(y)), CAR_SIZE)
            pygame.draw.circle(self.screen, (0,0,0), (int(x), int(y)), CAR_SIZE, 1) # Borda

    def update_animation(self):
        if self.anim_path and self.anim_index < len(self.anim_path) - 1:
            self.anim_progress += self.anim_speed
            
            start_node = self.anim_path[self.anim_index]
            end_node = self.anim_path[self.anim_index + 1]
            
            start_pos = self.transform_coord(start_node.coord)
            end_pos = self.transform_coord(end_node.coord)
            
            # Interpolação linear
            cur_x = start_pos[0] + (end_pos[0] - start_pos[0]) * self.anim_progress
            cur_y = start_pos[1] + (end_pos[1] - start_pos[1]) * self.anim_progress
            self.car_pos = (cur_x, cur_y)
            
            if self.anim_progress >= 1.0:
                self.anim_progress = 0.0
                self.anim_index += 1
        elif self.anim_path:
             # Fim da animação, manter carro no destino
             dest_node = self.anim_path[-1]
             self.car_pos = self.transform_coord(dest_node.coord)


    def run(self, algorithms=None, start_node="R1", end_node="R15"):
        path = None
        running = True
        
        print(f"Visualizador iniciado. Controlos:")
        print(f"  [U] - Executar UCS de {start_node} para {end_node}")
        print(f"  [ESC] - Sair")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    if algorithms:
                        algo_name = None
                        if event.key == pygame.K_u and 'UCS' in algorithms:
                            algo_name = 'UCS'
                        
                        if algo_name:
                            print(f"A executar {algo_name}...")
                            result = algorithms[algo_name](self.map_graph, start_node, end_node)
                            if result.path:
                                path = result.path
                                print(f"{algo_name} Caminho encontrado: {[p.get_name() for p in path]}")
                                print(f"Custo: {result.distance}, Visitados: {len(result.visited)}")
                                
                                # Iniciar animação
                                self.anim_path = result.path
                                self.anim_index = 0
                                self.anim_progress = 0.0
                            else:
                                print(f"{algo_name} não encontrou caminho.")
                                path = None
                                self.anim_path = None
                                self.car_pos = None

            self.update_animation()

            self.screen.fill(BG_COLOR)
            
            self.draw_edges()
            if path:
                self.draw_path(path)
            
            self.draw_nodes()
            
            # Desenhar Carro
            self.draw_car()
            
            # Desenhar Instruções da UI
            menu_text = f"U: UCS | {start_node} -> {end_node}"
            menu_surf = self.font.render(menu_text, True, (50, 50, 50))
            self.screen.blit(menu_surf, (10, 10))

            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
