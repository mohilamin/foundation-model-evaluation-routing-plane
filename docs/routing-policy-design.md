# Routing Policy Design

Routing uses hard constraints first and utility scoring second.

Steps:

1. Classify task, domain, and risk.
2. Filter unsupported models.
3. Enforce model class allowlist.
4. Apply safety gate.
5. Apply latency and cost constraints.
6. Apply minimum quality bar.
7. Score remaining candidates.
8. Select primary and fallback.
9. Write explanation.

If no model satisfies all constraints, the system routes to `fallback_model` and marks the decision as a constraint violation.
