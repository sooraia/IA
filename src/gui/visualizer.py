"""
Módulo de visualização gráfica da simulação usando pygame.
Este módulo fornece uma interface gráfica para visualizar o mapa da cidade,
os veículos em movimento e os caminhos calculados pelos diferentes algoritmos.
"""
import pygame
import sys
from src.graph.map import Map
from src.graph.place import PlaceType
from src.domain.structs import EstadoVeiculo

# Constantes de dimensão do ecrã (quadrado)
LARGURA_ECRA = 800
ALTURA_ECRA = 800

# ============================================================================
# CALIBRAÇÃO DO MAPA - Ajustar offset para alinhar com a imagem de fundo
# ============================================================================
# Offsets em pixels para deslocar todos os pontos
OFFSET_X = 50             # Deslocar horizontalmente (+direita, -esquerda)
OFFSET_Y = -50           # Deslocar verticalmente (+baixo, -cima)
# ============================================================================

# Cores de fundo e elementos
COR_FUNDO = (255, 255, 255)
RAIO_NO = 15
TAMANHO_FONTE = 12

# Cores dos diferentes tipos de locais
COR_RECOLHA = (100, 100, 255)           # Azul - pontos de recolha de passageiros
COR_ABASTECIMENTO = (100, 255, 100)     # Verde - postos de abastecimento
COR_CARREGAMENTO = (255, 165, 0)        # Laranja - estações de carregamento
COR_PADRAO = (200, 200, 200)            # Cinzento - outros locais
COR_ARESTA = (50, 50, 50)               # Cinzento escuro - arestas
COR_TEXTO = (0, 0, 0)                   # Preto - texto

# Estilos das estradas e caminhos
LARGURA_ESTRADA = 8
COR_ESTRADA = (100, 100, 100)
LARGURA_CAMINHO = 4
COR_CAMINHO = (255, 0, 0)               # Vermelho - caminho encontrado

# Configurações dos veículos
COR_CARRO = (100, 255, 100)           # Amarelo - veículo disponível
COR_CARRO_OCUPADO = (255, 100, 100)     # Vermelho - veículo ocupado
TAMANHO_CARRO = 12


class Visualizer:
    """
    Classe responsável pela visualização gráfica da simulação.
    Permite visualizar o mapa, os veículos e testar diferentes algoritmos de procura.
    """
    
    def __init__(self, map_graph: Map, estado=None):
        """
        Inicializa o visualizador.
        
        Args:
            map_graph: Instância do mapa com o grafo da cidade
            estado: Estado da simulação (opcional)
        """
        pygame.init()
        self.screen = pygame.display.set_mode((LARGURA_ECRA, ALTURA_ECRA))
        self.estado = estado
        pygame.display.set_caption("TaxiGreen AI - Visualização da Cidade")
        self.clock = pygame.time.Clock()
        self.map_graph = map_graph
        self.font = pygame.font.SysFont('Arial', TAMANHO_FONTE)
        
        # Calcular escala - o mapa ocupa todo o ecrã
        self.scale_x = LARGURA_ECRA / 10.0   # Coordenadas vão de 0 a ~10
        self.scale_y = ALTURA_ECRA / 10.0

        # Estado da animação
        self.anim_path = None           # Caminho a animar
        self.anim_index = 0             # Índice atual no caminho
        self.anim_progress = 0.0        # Progresso da animação (0.0 a 1.0)
        self.anim_speed = 0.05          # Velocidade da animação por frame
        self.car_pos = None             # Posição atual do carro na animação

        # Carregar recursos gráficos
        import os
        self.car_img = None
        self.bg_img = None
        
        gui_path = os.path.dirname(os.path.abspath(__file__))
        car_path = os.path.join(gui_path, "car.png")
        map_path = os.path.join(gui_path, "map.jpeg")

        try:
            if os.path.exists(car_path):
                raw_car = pygame.image.load(car_path)
                # Escalar o carro para um tamanho adequado
                self.car_img = pygame.transform.scale(raw_car, (40, 20))
            
            if os.path.exists(map_path):
                self.bg_img = pygame.image.load(map_path)
                self.bg_img = pygame.transform.scale(self.bg_img, (LARGURA_ECRA, ALTURA_ECRA))
        except Exception as e:
            print(f"Erro ao carregar imagens: {e}")

    def transform_coord(self, coord):
        """
        Transforma coordenadas do mapa para coordenadas do ecrã.
        """
        x, y = coord
        # Converter para pixels (Y invertido porque pygame tem origem no topo)
        screen_x = (x * self.scale_x) + OFFSET_X
        screen_y = ALTURA_ECRA - (y * self.scale_y) + OFFSET_Y
        return (screen_x, screen_y)

    def draw_edges(self):
        """
        Desenha todas as arestas (estradas) do grafo no ecrã.
        Inclui os pontos intermédios (cruzamentos) para um traçado mais realista.
        """
        drawn_edges = set()
        
        for node, edges in self.map_graph.graph.items():
            for (neighbor, tipo_zona, cruzamentos) in edges:
                # Evitar desenhar a mesma aresta duas vezes
                pair = tuple(sorted((node.get_name(), neighbor.get_name())))
                if pair in drawn_edges:
                    continue
                
                drawn_edges.add(pair)
                
                # Determinar cor com base no tipo de zona (cores premium)
                if tipo_zona == "Old town":
                    cor_estrada = (180, 140, 90)      # Dourado suave - centro histórico
                elif tipo_zona == "Residencial":
                    cor_estrada = (90, 160, 130)      # Verde esmeralda - residencial
                else:
                    cor_estrada = (130, 140, 160)     # Azul acinzentado - normal
                
                # Construir lista de todos os pontos da aresta
                pontos = [node.coord]
                if cruzamentos:
                    pontos.extend(cruzamentos)
                pontos.append(neighbor.coord)
                
                # Desenhar todas as secções da estrada
                for i in range(len(pontos) - 1):
                    start_pos = self.transform_coord(pontos[i])
                    end_pos = self.transform_coord(pontos[i + 1])
                    pygame.draw.line(self.screen, cor_estrada, start_pos, end_pos, LARGURA_ESTRADA)

    def draw_nodes(self):
        """
        Desenha todos os nós (locais) do grafo no ecrã.
        Cada tipo de local tem uma cor diferente.
        """
        for node in self.map_graph.places:
            pos = self.transform_coord(node.coord)
            
            # Determinar a cor com base no tipo de local
            color = COR_PADRAO
            if node.placeType == PlaceType.RECOLHA_DE_PASSAGEIROS:
                color = COR_RECOLHA
            elif node.placeType == PlaceType.POSTO_DE_ABASTECIMENTO:
                color = COR_ABASTECIMENTO
            elif node.placeType == PlaceType.ESTACAO_DE_CARGA:
                color = COR_CARREGAMENTO
            
            # Desenhar o círculo do local
            pygame.draw.circle(self.screen, color, (int(pos[0]), int(pos[1])), RAIO_NO)
            pygame.draw.circle(self.screen, (0,0,0), (int(pos[0]), int(pos[1])), RAIO_NO, 1)  # Borda
            
            # Desenhar o nome do local
            text_surf = self.font.render(node.get_name(), True, COR_TEXTO)
            text_rect = text_surf.get_rect(center=(int(pos[0]), int(pos[1])))
            self.screen.blit(text_surf, text_rect)

    def draw_path(self, path):
        """
        Desenha o caminho encontrado pelo algoritmo de procura.
        
        Args:
            path: Lista de nós que formam o caminho
        """
        if not path or len(path) < 2:
            return
            
        for i in range(len(path) - 1):
            start_node = path[i]
            end_node = path[i+1]
            
            start_pos = self.transform_coord(start_node.coord)
            end_pos = self.transform_coord(end_node.coord)
            
            # Desenhar linha do caminho (mais fina que a estrada)
            pygame.draw.line(self.screen, COR_CAMINHO, start_pos, end_pos, LARGURA_CAMINHO)

    def draw_vehicles(self):
        """
        Desenha todos os veículos da simulação no ecrã.
        A cor indica o estado do veículo (disponível, ocupado, a abastecer).
        """
        # Desenhar veículos da simulação se disponíveis
        if self.estado:
            for veiculo in self.estado.veiculos:
                pos = veiculo.posicao
                screen_pos = self.transform_coord(pos)
                
                # Determinar cor com base no estado do veículo
                color = COR_CARRO
                if veiculo.estado == EstadoVeiculo.OCUPADO:
                    color = COR_CARRO_OCUPADO
                elif veiculo.estado == EstadoVeiculo.ABASTECER:
                    color = (0, 0, 255)  # Azul - a abastecer
                
                # Desenhar o veículo
                if self.car_img:
                    # Centrar a imagem na posição
                    dest_rect = self.car_img.get_rect(center=(int(screen_pos[0]), int(screen_pos[1])))
                    self.screen.blit(self.car_img, dest_rect)
                    
                    # Indicador de estado (pequeno círculo colorido)
                    pygame.draw.circle(self.screen, color, (int(screen_pos[0]) + 15, int(screen_pos[1]) - 10), 4)
                else:
                    pygame.draw.circle(self.screen, color, (int(screen_pos[0]), int(screen_pos[1])), TAMANHO_CARRO)
                    pygame.draw.circle(self.screen, (0,0,0), (int(screen_pos[0]), int(screen_pos[1])), TAMANHO_CARRO, 1)
                
                # Desenhar identificador do veículo
                id_surf = self.font.render(veiculo.id.split('-')[1], True, (0,0,0))
                self.screen.blit(id_surf, (int(screen_pos[0])-5, int(screen_pos[1])-20))

        # Desenhar também o carro de demonstração se estiver a animar um caminho
        if self.car_pos:
            x, y = self.car_pos
            if self.car_img:
                 dest_rect = self.car_img.get_rect(center=(int(x), int(y)))
                 self.screen.blit(self.car_img, dest_rect)
            else:
                pygame.draw.circle(self.screen, (200, 200, 200), (int(x), int(y)), TAMANHO_CARRO - 2)
                pygame.draw.circle(self.screen, (0,0,0), (int(x), int(y)), TAMANHO_CARRO - 2, 1)

    def update_animation(self):
        """
        Atualiza a animação do carro a percorrer o caminho.
        """
        if self.anim_path and self.anim_index < len(self.anim_path) - 1:
            self.anim_progress += self.anim_speed
            
            start_node = self.anim_path[self.anim_index]
            end_node = self.anim_path[self.anim_index + 1]
            
            start_pos = self.transform_coord(start_node.coord)
            end_pos = self.transform_coord(end_node.coord)
            
            # Interpolação linear entre as posições
            cur_x = start_pos[0] + (end_pos[0] - start_pos[0]) * self.anim_progress
            cur_y = start_pos[1] + (end_pos[1] - start_pos[1]) * self.anim_progress
            self.car_pos = (cur_x, cur_y)
            
            if self.anim_progress >= 1.0:
                self.anim_progress = 0.0
                self.anim_index += 1
        elif self.anim_path:
             # Fim da animação - manter carro no destino
             dest_node = self.anim_path[-1]
             self.car_pos = self.transform_coord(dest_node.coord)


    def run(self, nome_algoritmo=""):
        """
        Executa o loop principal do visualizador.
        
        Args:
            nome_algoritmo: Nome do algoritmo em uso na simulação
        """
        running = True
        
        print(f"Visualizador iniciado. Controlos:")
        print(f"  [R] - Reiniciar simulação")
        print(f"  [ESC] - Sair")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    # Tecla R para reiniciar a simulação
                    if event.key == pygame.K_r and self.estado:
                         print("A reiniciar simulação...")
                         self.estado.reset()
                         
                         # Reimportar dependências necessárias para reinício
                         from src.search.iterative import iterative
                         from src.search.heuristics import distance_heuristic
                         import threading
                         
                         t = threading.Thread(target=self.estado.run, args=(iterative, distance_heuristic))
                         t.daemon = True
                         t.start()

            # Desenhar fundo
            if self.bg_img:
                self.screen.blit(self.bg_img, (0, 0))
            else:
                self.screen.fill(COR_FUNDO)
            
            # Desenhar elementos do mapa
            self.draw_edges()
            self.draw_nodes()
            self.draw_vehicles()
            
            # Desenhar informações da simulação
            if self.estado:
                # Nome do algoritmo (canto superior esquerdo)
                algo_text = f"Algoritmo: {nome_algoritmo}"
                algo_surf = self.font.render(algo_text, True, (0, 0, 0))
                # Fundo semi-transparente para o texto
                pygame.draw.rect(self.screen, (255, 255, 255, 200), (5, 5, algo_surf.get_width() + 10, 25))
                self.screen.blit(algo_surf, (10, 10))
                
                # Estado da simulação
                status_text = f"Pedidos: {self.estado.pedidos_completados}/{self.estado.max_pedidos}"
                status_surf = self.font.render(status_text, True, (0, 0, 0))
                pygame.draw.rect(self.screen, (255, 255, 255, 200), (5, 30, status_surf.get_width() + 10, 25))
                self.screen.blit(status_surf, (10, 35))
                
                # Instrução de reinício
                reset_text = "[R] Reiniciar  [ESC] Sair"
                reset_surf = self.font.render(reset_text, True, (100, 100, 100))
                pygame.draw.rect(self.screen, (255, 255, 255, 200), (5, 55, reset_surf.get_width() + 10, 25))
                self.screen.blit(reset_surf, (10, 60))

            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()

