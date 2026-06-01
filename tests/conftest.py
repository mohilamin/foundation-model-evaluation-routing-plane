"""Shared test setup."""

import pytest

from src.routing_plane_core import run_pipeline


@pytest.fixture(scope="session", autouse=True)
def generated_artifacts() -> dict:
    """Generate deterministic artifacts once for the test session."""
    return run_pipeline()
