"""Model metadata helpers."""

from src.routing_plane_core import model_specs


def list_model_metadata() -> list[dict]:
    """Return model metadata dictionaries."""
    return [spec.__dict__ for spec in model_specs()]
