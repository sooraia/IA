# TaxiGreen AI

Este projeto simula uma frota de táxis elétricos autónomos utilizando vários algoritmos de pesquisa de IA. Inclui um visualizador para monitorizar a simulação e depurar algoritmos de procura de caminhos.

## Pré-requisitos

- Python 3.x
- Pygame (instalado no ambiente virtual)

## Configuração

Um ambiente virtual (`venv`) já foi criado na raiz do projeto.

## Executar a Aplicação

Para correr a simulação com o visualizador GUI, execute o seguinte comando a partir da raiz do projeto:

```bash
./venv/bin/python src/main.py
```

### Controlos da GUI

- **Simulação**: A simulação corre automaticamente em segundo plano. Os veículos (carros) aparecerão no mapa a atender pedidos.
- **Reiniciar**: Pressione **`R`** para reiniciar a simulação.
- **Visualização de Pesquisa Manual**: Pressione as seguintes teclas para visualizar algoritmos de procura específicos sobre o mapa:
  - **`U`**: Pesquisa de Custo Uniforme (UCS)
  - **`B`**: Pesquisa em Largura (BFS)
  - **`D`**: Pesquisa em Profundidade (DFS)
  - **`A`**: Pesquisa A*
  - **`G`**: Pesquisa Gulosa (Greedy)
  - **`I`**: Aprofundamento Iterativo
  - **`F`**: DFS Iterativo
- **Sair**: Pressione **`ESC`** ou feche a janela.

## Estrutura do Projeto

- `src/domain/` – Representações de estado para veículos, pedidos, mapas.
- `src/search/` – Algoritmos de pesquisa (UCS, A*, BFS, DFS, etc.).
- `src/gui/` – Lógica de visualização utilizando Pygame.
- `src/data/` – Ficheiros de configuração (ex: definições de veículos).
- `src/main.py` – Ponto de entrada da aplicação.
