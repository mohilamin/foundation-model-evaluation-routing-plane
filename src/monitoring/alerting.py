"""Alerting helpers."""


def should_alert(score: float) -> bool:
    """Return true when health score should alert."""
    return score < 75
