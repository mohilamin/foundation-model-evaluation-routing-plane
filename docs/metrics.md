# Metrics

Core metrics:

- `quality_score`: simulated task answer quality.
- `safety_pass_rate`: percentage of safety-required tasks passing safety threshold.
- `average_latency_ms`: mean simulated latency.
- `average_cost_usd`: mean simulated request cost.
- `reliability_score`: simulated availability and error resilience.
- `overall_model_utility_score`: weighted quality, safety, reliability, latency, and cost score.
- `routing_success_rate`: percent of decisions without hard constraint violation.
- `fallback_rate`: percent routed to fallback model.
- `deployment_readiness_score`: percent of deployment checks passing.
