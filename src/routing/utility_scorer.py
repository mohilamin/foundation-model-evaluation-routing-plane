"""Routing utility scoring."""


def route_utility(quality: float, safety: float, reliability: float, latency: float, cost: float) -> float:
    """Calculate routing utility."""
    return round(quality * 0.34 + safety * 0.26 + reliability * 0.18 + latency * 0.12 + cost * 0.10, 4)
