# TaxiGreen AI

Este projeto simula uma frota de táxis elétricos autónomos utilizando vários algoritmos de pesquisa de IA. Inclui um visualizador para monitorizar a simulação e depurar algoritmos de procura de caminhos.

## Pré-requisitos

- Python 3.10+
- Dependências listadas em `requirements.txt`

## Executar a Aplicação

Para correr a simulação com o visualizador GUI, execute o seguinte comando a partir da raiz do projeto:

```bash
python src/main.py
```

## Estrutura do Projeto

A estrutura do código fonte (`src/`) organiza-se da seguinte forma:

- `src/domain/` – Representações de estado para veículos, pedidos, mapas e outras entidades principais.
- `src/search/` – Estratégias de pesquisa (informada e não informada) e heurísticas.
- `src/simulation/` – Ambiente de simulação dinâmico, agendamento de eventos e execução de cenários.
- `src/gui/` – Interface gráfica e visualização utilizando Pygame.
- `src/metrics/` – Métricas de avaliação e análises dos resultados da simulação.
- `src/data/` – Carregadores, analisadores e geradores de dados (e.g., config de veículos).
- `src/config/` – Primitivas de configuração e templates de cenários.
- `src/utils/` – Utilitários transversais (tempo, geografia, logs, etc.).
- `src/main.py` – Ponto de entrada principal da aplicação.
