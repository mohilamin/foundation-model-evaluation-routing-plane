"""Metric helpers."""


def weighted_utility(quality: float, safety: float, reliability: float, latency_score: float, cost_score: float) -> float:
    """Calculate weighted utility."""
    return round(quality * 0.35 + safety * 0.25 + reliability * 0.2 + latency_score * 0.1 + cost_score * 0.1, 4)
