"""Model health helpers."""


def health_status(score: float) -> str:
    """Map a health score to status."""
    return "healthy" if score >= 85 else "watch"
