"""Helper functions for charting."""

# pylint: disable=R0917

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame, Series


def get_charting_functions(view: type) -> dict[str, Callable]:
    """Discover charting functions."""
    # pylint: disable=import-outside-toplevel
    from inspect import getmembers, getsource, isfunction

    implemented_functions: dict[str, Callable] = {}

    for name, obj in getmembers(view, isfunction):
        if (
            obj.__module__ == view.__module__
            and not name.startswith("_")
            and "NotImplementedError" not in getsource(obj)
        ):
            implemented_functions[name] = obj

    return implemented_functions


def get_charting_functions_list(view: type) -> list[str]:
    """Get a list of all the charting functions."""
    return list(get_charting_functions(view).keys())


def z_score_standardization(data: "Series") -> "Series":
    """Z-Score Standardization Method."""
    return (data - data.mean()) / data.std()


def calculate_returns(data: "Series") -> "Series":
    """Calculate the returns of a column."""
    return ((1 + data.pct_change(fill_method=None).fillna(0)).cumprod() - 1) * 100


def should_share_axis(
    df: "DataFrame", col1: str, col2: str, threshold: float = 0.15
) -> bool:
    """Determine whether two columns should share an axis."""
    # pylint: disable=import-outside-toplevel
    from pandas import Series

    try:
        if isinstance(df, Series):
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


def heikin_ashi(data: "DataFrame") -> "DataFrame":
    """Return OHLC data as Heikin Ashi Candles.

    Parameters
    ----------
    data: DataFrame
        DataFrame containing OHLC data.

    Returns
    -------
    DataFrame
        DataFrame copy with Heikin Ashi candle calculations.
    """
    # pylint: disable=import-outside-toplevel
    from pandas_ta import candles

    df = data.copy()

    check_columns = ["open", "high", "low", "close"]

    for item in check_columns:
        if item not in df.columns:
            raise ValueError(
                f"The expected column labels, {check_columns}, were not found in DataFrame."
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
