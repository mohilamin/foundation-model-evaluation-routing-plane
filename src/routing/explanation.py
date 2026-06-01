"""Routing explanation helpers."""


def explain(selected_model: str, reason: str) -> dict:
    """Build a minimal routing explanation."""
    return {"selected_model": selected_model, "reason": reason}
