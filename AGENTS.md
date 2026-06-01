# AGENTS.md

You are building a production-style AI/ML infrastructure project.

Project name:
Foundation Model Evaluation & Routing Control Plane

Primary goal:
Build a local prototype that simulates how enterprise AI teams evaluate, compare, route, and monitor multiple model candidates under quality, latency, cost, safety, reliability, and business constraints.

## Core Outcome

The system should answer:

"Which model should handle this request, why, and what tradeoffs were considered?"

## Build Principles

- Use Python 3.12.
- Write clean, modular, typed Python.
- Use docstrings for public functions.
- Use structured logging.
- Add error handling.
- Use synthetic data only.
- Do not use real sensitive data.
- Do not call paid/external model APIs in V0.1.
- Keep V0.1 deterministic and locally runnable.
- Every model must have metadata.
- Every model evaluation must generate scorecards.
- Every routing decision must include an explanation.
- Every high-risk route must pass safety constraints.
- Every fallback decision must be logged.
- Dashboard must be demo-ready.
- API must return valid JSON.
- Tests and ruff must pass.

## Commit Message Requirements

- Do not use generic commit messages such as "Build project," "Create files," or "Build router."
- Use professional scoped commit messages.
- Prefer Conventional Commit style:
  - feat(evals): add evaluation dataset generator
  - feat(router): add constraint-aware routing engine
  - feat(scorecards): generate model performance scorecards
  - feat(api): expose routing endpoints
  - feat(dashboard): add model routing control plane dashboard
  - docs(readme): document deployment workflow

## Definition of Done

A task is complete only when:
- project runs locally
- synthetic evaluation data exists
- model registry exists
- model scorecards exist
- routing decisions exist
- canary/shadow reports exist
- Pareto frontier report exists
- API launches
- dashboard launches
- Docker exists
- CI exists
- tests pass
- ruff passes
- README is detailed and diagram-rich
- deployment docs exist
- no real sensitive data is used
