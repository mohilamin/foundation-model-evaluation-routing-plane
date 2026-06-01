"""Cost latency helpers."""


def latency_score(latency_ms: float, budget_ms: float) -> float:
    """Calculate normalized latency score."""
    return max(0.0, min(1.0, 1 - latency_ms / budget_ms))
