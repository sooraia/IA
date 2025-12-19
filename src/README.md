# TaxiGreen Source Layout

This package is organised to map directly to the project deliverables:

- `domain/` – State representations for vehicles, requests, depots, and other core entities.
- `search/` – Search strategies (uninformed and informed) plus heuristics.
- `simulation/` – Dynamic simulation environment, event scheduling, and scenario runners.
- `metrics/` – Evaluation metrics and analytics on simulation outcomes.
- `data/` – Loaders, parsers, and synthetic data generators.
- `config/` – Shared configuration primitives and scenario templates.
- `utils/` – Cross-cutting helpers (time, geography, logging, etc.).

Each subpackage currently contains an empty `__init__.py` to declare the module; add the actual implementations as the work advances.
