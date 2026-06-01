# Technical Deep Dive

The runtime uses deterministic simulation to avoid external APIs while preserving production-style architecture. The central pipeline generates tasks, model metadata, simulated outputs, evaluation reports, routing decisions, Pareto analysis, canary/shadow reports, monitoring reports, and a DuckDB warehouse.

The routing engine treats safety, task support, domain support, latency, cost, and quality as hard constraints before scoring utility. This mirrors production model gateways where governance requirements must precede ranking.

In production, simulated providers could be replaced with OpenAI, Anthropic, Gemini, open-source model servers, MLflow, LiteLLM, OpenTelemetry, and real traffic logs.
