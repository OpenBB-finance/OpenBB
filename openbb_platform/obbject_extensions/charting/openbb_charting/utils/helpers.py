"""Helper functions for charting."""

from inspect import getmembers, getsource, isfunction
from typing import List

import pandas as pd

from openbb_charting import charting_router


def get_charting_functions() -> List[str]:
    """Discover charting functions."""
    implemented_functions = []

    for name, obj in getmembers(charting_router, isfunction):
        if (
            obj.__module__ == charting_router.__name__
            and not name.startswith("_")
            and "NotImplementedError" not in getsource(obj)
        ):
            implemented_functions.append(name)

    return implemented_functions


def z_score_standardization(data: pd.Series) -> pd.Series:
    """Z-Score Standardization Method."""
    return (data - data.mean()) / data.std()


def calculate_returns(data: pd.Series) -> pd.Series:
    """Calculate the returns of a column."""
    return ((1 + data.pct_change().dropna()).cumprod() - 1) * 100


def should_share_axis(
    df: pd.DataFrame, col1: str, col2: str, threshold: float = 0.15
) -> bool:
    """Determine whether two columns should share an axis."""
    range1 = df[col1].max() - df[col1].min()
    range2 = df[col2].max() - df[col2].min()
    # Calculate the ratio of the two ranges
    ratio = max(range1, range2) / min(range1, range2)
    # If the ratio is less than the threshold, the two columns can share an axis
    return ratio < threshold
