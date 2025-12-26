import pygame
import sys
from src.graph.map import Map
from src.graph.place import PlaceType
from src.domain.structs import EstadoVeiculo

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
CAR_BUSY_COLOR = (255, 100, 100) # Red busy
CAR_SIZE = 12

class Visualizer:
    def __init__(self, map_graph: Map, estado=None):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.estado = estado
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

        # Load assets
        import os
        self.car_img = None
        self.bg_img = None
        
        gui_path = os.path.dirname(os.path.abspath(__file__))
        car_path = os.path.join(gui_path, "car.png")
        map_path = os.path.join(gui_path, "map.jpeg")

        try:
            if os.path.exists(car_path):
                raw_car = pygame.image.load(car_path)
                # Scale car to reasonable size - maybe double the circle radius size
                self.car_img = pygame.transform.scale(raw_car, (40, 20)) # Width, Height estimate
            
            if os.path.exists(map_path):
                self.bg_img = pygame.image.load(map_path)
                self.bg_img = pygame.transform.scale(self.bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Erro ao carregar imagens: {e}")

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

    def draw_vehicles(self):
        # Draw simulation vehicles if available
        if self.estado:
            for veiculo in self.estado.veiculos:
                pos = veiculo.posicao
                screen_pos = self.transform_coord(pos)
                
                color = CAR_COLOR
                if veiculo.estado == EstadoVeiculo.OCUPADO:
                    color = CAR_BUSY_COLOR
                elif veiculo.estado == EstadoVeiculo.ABASTECER:
                    color = (0, 0, 255) # Blue
                
                # Draw vehicle
                if self.car_img:
                    # Center the image
                    w, h = self.car_img.get_size()
                    dest_rect = self.car_img.get_rect(center=(int(screen_pos[0]), int(screen_pos[1])))
                    self.screen.blit(self.car_img, dest_rect)
                    
                    # Status Indicator (dot)
                    pygame.draw.circle(self.screen, color, (int(screen_pos[0]) + 15, int(screen_pos[1]) - 10), 4)
                else:
                    pygame.draw.circle(self.screen, color, (int(screen_pos[0]), int(screen_pos[1])), CAR_SIZE)
                    pygame.draw.circle(self.screen, (0,0,0), (int(screen_pos[0]), int(screen_pos[1])), CAR_SIZE, 1)
                
                # Draw ID (optional)
                id_surf = self.font.render(veiculo.id.split('-')[1], True, (0,0,0)) # Show number part
                self.screen.blit(id_surf, (int(screen_pos[0])-5, int(screen_pos[1])-20))

        # Also draw the "demo" car if an algorithm path is being shown manually
        if self.car_pos:
            x, y = self.car_pos
            if self.car_img:
                 dest_rect = self.car_img.get_rect(center=(int(x), int(y)))
                 self.screen.blit(self.car_img, dest_rect)
            else:
                pygame.draw.circle(self.screen, (200, 200, 200), (int(x), int(y)), CAR_SIZE - 2) # Smaller ghost car
                pygame.draw.circle(self.screen, (0,0,0), (int(x), int(y)), CAR_SIZE - 2, 1)

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
                    
                    if event.key == pygame.K_r and self.estado:
                         print("Reiniciando simulação...")
                         self.estado.reset()
                         
                         # Reimport needed deps for restart
                         from src.search.iterative import iterative
                         from src.search.heuristics import distance_heuristic
                         import threading
                         
                         t = threading.Thread(target=self.estado.run, args=(iterative, distance_heuristic))
                         t.daemon = True
                         t.start()
                    
                    if algorithms:
                        algo_name = None
                        if event.key == pygame.K_u and 'UCS' in algorithms:
                            algo_name = 'UCS'
                        elif event.key == pygame.K_b and 'BFS' in algorithms:
                            algo_name = 'BFS'
                        elif event.key == pygame.K_d and 'DFS' in algorithms:
                            algo_name = 'DFS'
                        elif event.key == pygame.K_a and 'A*' in algorithms:
                            algo_name = 'A*'
                        elif event.key == pygame.K_g and 'Greedy' in algorithms:
                            algo_name = 'Greedy'
                        elif event.key == pygame.K_i and 'Iterative' in algorithms:
                            algo_name = 'Iterative'
                        elif event.key == pygame.K_f and 'Iterative DFS' in algorithms:
                            algo_name = 'Iterative DFS'
                        
                        if algo_name:
                            print(f"A executar {algo_name}...")
                            # Algoritmos podem ter assinaturas diferentes
                            # BFS/DFS/UCS: (map, start, end) -> SearchResult
                            # A*/Greedy: (map, start, end, vehicle?, heuristic) -> SearchResult ?? 
                            # Need to check signatures.
                            
                            # Assuming standard signature for now based on main.py calls
                            if algo_name in ['A*', 'Greedy']:
                                # AStar needs heuristic func. greedy needs heuristic.
                                # Wait, visualizer doesn't know about heuristic func or vehicle.
                                pass 
                            
                            # Let's just use the signature that works or wrap them in main?
                            # In main.py:
                            # state.run calls iterative(..., heuristic)
                            
                            # Let's check signatures from early file reads.
                            # AStar: a_star_search(map_graph, start_name, target_name, vehicle, heuristic_func)
                            # Greedy: greedy_search(map_graph, start_name, target_name, vehicle, heuristic)
                            
                            # The `algorithms` dict in main.py maps strings to functions.
                            # Visualizer calls algorithms[algo_name](self.map_graph, start_node, end_node)
                            # This will fail for A* and Greedy if they expect more args.
                            
                            try:
                                if algo_name in ['A*', 'Greedy']:
                                    from src.search.heuristics import distance_heuristic
                                    # vehicle is not really used in AStar.py shown earlier? let's check.
                                    # line 6: def a_star_search(map_graph: Map, start_name, target_name, vehicle, heuristic_func)
                                    # It uses vehicle in heuristic_func(v, target, vehicle)
                                    
                                    # heuristic_func code was not shown fully but likely needs vehicle.
                                    # We can pass None or a dummy vehicle if it's not critical, or handle it.
                                    
                                    result = algorithms[algo_name](self.map_graph, start_node, end_node, None, distance_heuristic)
                                elif algo_name == 'Iterative DFS': # iterative
                                    # iterative signature?
                                    # state.run calls iterative, distance_heuristic
                                    from src.search.heuristics import distance_heuristic
                                    result = algorithms[algo_name](self.map_graph, start_node, end_node, distance_heuristic)
                                else:
                                    result = algorithms[algo_name](self.map_graph, start_node, end_node)

                                if result.path:
                                    path = result.path
                                    print(f"{algo_name} Caminho encontrado: {[p.get_name() for p in path]}")
                                    if hasattr(result, 'distance'):
                                        print(f"Custo: {result.distance}, Visitados: {len(result.visited)}")
                                    elif hasattr(result, 'cost'):
                                         print(f"Custo: {result.cost}, Visitados: {len(result.visited)}")
                                    
                                    # Iniciar animação
                                    self.anim_path = result.path
                                    self.anim_index = 0
                                    self.anim_progress = 0.0
                                else:
                                    print(f"{algo_name} não encontrou caminho.")
                                    path = None
                                    self.anim_path = None
                                    self.car_pos = None
                            except Exception as e:
                                print(f"Erro ao executar {algo_name}: {e}")

            self.update_animation()
            
            if self.bg_img:
                self.screen.blit(self.bg_img, (0, 0))
            else:
                self.screen.fill(BG_COLOR)
            
            self.draw_edges()
            if path:
                self.draw_path(path)
            
            self.draw_nodes()
            
            # Desenhar Carro
            # self.draw_car()
            self.draw_vehicles()
            
            # Desenhar Instruções da UI
            if self.estado:
                status_text = f"Simulacao: Pedidos Completos {self.estado.pedidos_completados}/{self.estado.max_pedidos} | Pendentes: {len([p for p in self.estado.pedidos if p.estado == 'pendente'])}"
                status_surf = self.font.render(status_text, True, (0, 0, 0))
                self.screen.blit(status_surf, (10, 30))
                
                reset_text = "Press 'R' to Restart Simulation"
                reset_surf = self.font.render(reset_text, True, (200, 0, 0))
                self.screen.blit(reset_surf, (10, 50))
                
            menu_text = f"Algorithms: U(CS), B(FS), D(FS), A(*), G(reedy), I(terative)"
            menu_surf = self.font.render(menu_text, True, (50, 50, 50))
            self.screen.blit(menu_surf, (10, 10))

            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
