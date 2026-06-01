"""Regression evaluation helpers."""


def regression_flag(delta: float, threshold: float = -0.03) -> bool:
    """Return true when a metric delta is a regression."""
    return delta < threshold
