"""Helper functions for charting."""

from inspect import getmembers, getsource, isfunction
from typing import Callable, Dict, List, Type, Union

import pandas as pd
from pandas_ta import candles


def get_charting_functions(
    accessor: Type, with_objects: bool = False
) -> Union[List[str], Dict[str, Callable]]:
    """Discover charting functions."""
    implemented_functions: Union[List[str], Dict[str, Callable]] = (
        [] if not with_objects else {}
    )

    for name, obj in getmembers(accessor, isfunction):
        if (
            obj.__module__ == accessor.__module__
            and not name.startswith("_")
            and "NotImplementedError" not in getsource(obj)
        ):
            if with_objects:
                implemented_functions[name] = obj
            else:
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
    try:
        if isinstance(df, pd.Series):
            df = df.to_frame()
        range1 = df[col1].max() - df[col1].min()
        range2 = df[col2].max() - df[col2].min()
        # Calculate the ratio of the two ranges
        ratio = max(range1, range2) / min(range1, range2)
        # If the ratio is less than the threshold, the two columns can share an axis
        if ratio == 1:
            return True
        return ratio < threshold
    except Exception:
        return False


def heikin_ashi(data: pd.DataFrame) -> pd.DataFrame:
    """Return OHLC data as Heikin Ashi Candles.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame containing OHLC data.

    Returns
    -------
    pd.DataFrame
        DataFrame copy with Heikin Ashi candle calculations.
    """
    df = data.copy()

    check_columns = ["open", "high", "low", "close"]

    for item in check_columns:
        if item not in df.columns:
            raise ValueError(
                "The expected column labels, "
                f"{check_columns}"
                ", were not found in DataFrame."
            )

    ha = candles.ha(
        df["open"],
        df["high"],
        df["low"],
        df["close"],
    )

    for item in check_columns:
        df[item] = ha[f"HA_{item}"]

    return df


def duration_sorter(durations: list) -> list:
    """Sort durations labeled as month_5, year_5, etc."""

    def duration_to_months(duration):
        """Convert duration to months."""
        if duration == "long_term":
            return 360
        parts = duration.split("_")
        months = 0
        for i in range(0, len(parts), 2):
            number = int(parts[i + 1])
            if parts[i] == "year":
                number *= 12  # Convert years to months
            months += number
        return months

    return sorted(durations, key=duration_to_months)
