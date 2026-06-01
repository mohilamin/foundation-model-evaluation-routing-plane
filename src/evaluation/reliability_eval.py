"""Reliability evaluation helpers."""


def reliability_status(score: float) -> str:
    """Map a reliability score to a status label."""
    return "healthy" if score >= 0.95 else "watch" if score >= 0.9 else "degraded"
