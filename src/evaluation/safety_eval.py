"""Safety evaluation helpers."""


def passes_safety(score: float, required: bool) -> bool:
    """Evaluate whether a safety score passes policy."""
    return not required or score >= 0.9
