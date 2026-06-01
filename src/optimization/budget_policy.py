"""Budget policy helpers."""


def within_budget(cost: float, budget: float) -> bool:
    """Return true when cost is within budget."""
    return cost <= budget
