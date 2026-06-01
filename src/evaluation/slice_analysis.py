"""Slice analysis helpers."""

import pandas as pd


def slice_count(df: pd.DataFrame, column: str) -> int:
    """Return number of distinct values in a slice column."""
    return int(df[column].nunique())
