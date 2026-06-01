"""Constraint filtering helpers."""


def satisfies_constraint(value: float, maximum: float) -> bool:
    """Return true when a value fits a maximum constraint."""
    return value <= maximum
