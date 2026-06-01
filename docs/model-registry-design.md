# Model Registry Design

The registry stores ten simulated model candidates with metadata for supported tasks, domains, quality profile, latency, cost, safety, reliability, stage, owner, version, and limitations.

Generated artifacts:

- `config/model_registry.yaml`
- `data/model_outputs/model_registry.csv`
- `data/model_outputs/model_cards/*.md`

Each model card describes intended use, profile tradeoffs, and limitations.
