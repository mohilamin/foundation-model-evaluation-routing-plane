"""Model registry access."""

from src.routing_plane_core import load_registry


def get_model_registry():
    """Return model registry records."""
    return load_registry()
