"""Model card helpers."""

from pathlib import Path

from src.routing_plane_core import DATA


def model_card_path(model_id: str) -> Path:
    """Return the local model card path."""
    return DATA / "model_outputs" / "model_cards" / f"{model_id}.md"
