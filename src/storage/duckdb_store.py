"""DuckDB warehouse loader."""

from src.routing_plane_core import load_duckdb_store


def load_store() -> dict:
    """Load generated artifacts into DuckDB."""
    return load_duckdb_store()
