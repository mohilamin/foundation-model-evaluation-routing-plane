# Design Decisions

## Decision: Synthetic data

Context:
The repo needs to be public and safe to run.

Options considered:
- Use production data
- Use anonymized samples
- Generate synthetic data

Choice made:
Generate synthetic data.

Why:
It makes the project shareable without privacy or security risk.

Tradeoff:
The data cannot capture every real-world edge case.

Production version:
Use approved data connectors, masking, privacy reviews, and controlled environments.

## Decision: Local-first runtime

Context:
Reviewers should be able to run the system without cloud setup.

Options considered:
- Cloud-native service
- Local prototype
- Notebook only

Choice made:
Local prototype with repo-native commands.

Why:
It lowers review friction and keeps validation repeatable.

Tradeoff:
It does not prove cloud scale.

Production version:
Deploy with managed compute, IaC, observability, and release controls.

## Decision: Deterministic simulation

Context:
The project should not depend on paid APIs or nondeterministic outputs.

Options considered:
- Live LLM/API calls
- Random simulation
- Deterministic simulation

Choice made:
Deterministic simulation.

Why:
It makes tests and scorecards stable.

Tradeoff:
It simplifies uncertainty and provider behavior.

Production version:
Add live adapters behind policy, tracing, retries, and evaluation gates.

## Decision: Scorecards as evidence

Context:
A reviewer needs proof beyond a dashboard screenshot.

Options considered:
- Dashboard only
- Logs only
- Versioned scorecards

Choice made:
Generate scorecards and reports.

Why:
They make validation inspectable and comparable.

Tradeoff:
Scorecards can oversimplify context.

Production version:
Add monitored production metrics, alerts, and trend analysis.

## Decision: FastAPI and Streamlit

Context:
The repo should show both service and review surfaces.

Options considered:
- CLI only
- Dashboard only
- API plus dashboard

Choice made:
FastAPI plus Streamlit where relevant.

Why:
It demonstrates serving and stakeholder review patterns.

Tradeoff:
It is not a hardened frontend/backend stack.

Production version:
Add auth, API gateway, frontend controls, and production deployment.

## Decision: DuckDB/local artifacts

Context:
The project needs a warehouse-like layer without external services.

Options considered:
- Cloud warehouse
- SQLite
- DuckDB/local CSV/JSON

Choice made:
Use local artifacts and DuckDB where relevant.

Why:
It keeps the system portable and queryable.

Tradeoff:
It does not represent distributed warehouse operations.

Production version:
Move to Snowflake, BigQuery, Databricks, or lakehouse storage.

## Decision: Modular Python structure

Context:
The system should be readable as architecture, not a single script.

Options considered:
- Notebook
- Single script
- Package modules

Choice made:
Use package modules by concern.

Why:
It makes source code review easier.

Tradeoff:
Some modules are intentionally thin wrappers in a prototype.

Production version:
Split services, shared libraries, orchestration, and integration packages.

## Decision: Tests and Ruff

Context:
A portfolio repo needs evidence that basic behavior is protected.

Options considered:
- Manual checks
- Unit/integration tests
- CI-only checks

Choice made:
Use pytest and Ruff.

Why:
They catch regressions and style issues.

Tradeoff:
Tests cover the simulated system, not production integrations.

Production version:
Add contract tests, integration tests, load tests, and security checks.

## Decision: No external API dependency

Context:
The repo should run without secrets.

Options considered:
- Require API keys
- Mock all providers
- Use deterministic local behavior

Choice made:
No external API dependency by default.

Why:
It avoids broken demos and secret handling risk.

Tradeoff:
It cannot demonstrate live provider failures.

Production version:
Add optional provider adapters with fallbacks and governance controls.
