# Future Enhancement Readiness

This document explains the lightweight future-enhancement scorecard added for `foundation-model-evaluation-routing-plane`.

The scorecard does not claim production readiness. It checks whether the repo has enough roadmap, validation, review, and deployment signals to make future work easier to prioritize.

Run:

```bash
python scripts/generate_future_enhancement_scorecard.py
```

Outputs:

- `data/scorecards/future_enhancement_readiness.json`
- `data/scorecards/future_enhancement_readiness.csv`

Planned enhancement areas:

- real provider adapters
- MLflow/LiteLLM integration
- OpenTelemetry tracing
- tenant budget enforcement
- authenticated model gateway
