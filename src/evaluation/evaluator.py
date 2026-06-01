"""Evaluation harness entrypoint."""

from src.routing_plane_core import evaluate_models


def run_evaluation() -> dict:
    """Run model evaluation."""
    return evaluate_models()
