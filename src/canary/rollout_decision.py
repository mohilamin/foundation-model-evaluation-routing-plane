"""Rollout decision helpers."""


def rollout_label(regressions: int) -> str:
    """Choose rollout label from regression count."""
    return "limited_rollout" if regressions <= 2 else "no_rollout"
