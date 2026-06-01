"""Drift simulation helpers."""


def drift_status(rate: float) -> str:
    """Map a drift rate to status."""
    return "stable" if rate < 0.1 else "watch"
