"""Constraint-aware routing engine."""

from src.routing_plane_core import route_request


def route(payload: dict) -> dict:
    """Route a single request."""
    return route_request(payload)
