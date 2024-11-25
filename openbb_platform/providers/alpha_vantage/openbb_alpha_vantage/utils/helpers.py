"""Alpha Vantage Helpers Module."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from pandas import DataFrame

INTERVALS_DICT = {
    "m": "TIME_SERIES_INTRADAY",
    "d": "TIME_SERIES_DAILY",
    "W": "TIME_SERIES_WEEKLY",
    "M": "TIME_SERIES_MONTHLY",
}


def get_interval(value: str) -> str:
    """Get the intervals for the Alpha Vantage API."""
    intervals = {
        "m": "min",
        "d": "day",
        "W": "week",
        "M": "month",
    }

    return f"{value[:-1]}{intervals[value[-1]]}"


def extract_key_name(key):
    """Extract the alphabetical part of the key using regex."""
    # pylint: disable=import-outside-toplevel
    import re

    match = re.search(r"\d+\.\s+([a-z]+)", key, re.I)
    return match.group(1) if match else key


def filter_by_dates(
    data: List[Dict[str, Any]], start_date: datetime, end_date: datetime
) -> List[Dict[str, Any]]:
    """Filter the data by start and end dates."""
    return list(
        filter(
            lambda x: start_date
            <= datetime.strptime(x["date"], "%Y-%m-%d").date()
            <= end_date,
            data,
        )
    )


def calculate_adjusted_prices(
    df: "DataFrame", column: str, dividends: bool = False
) -> "DataFrame":
    """Calculate the split-adjusted prices, or split and dividend adjusted prices.

    Parameters
    ----------
    df: DataFrame
        DataFrame with unadjusted OHLCV values + split_factor + dividend
    column: str
        The column name to adjust.
    dividends: bool
        Whether to adjust for both splits and dividends. Default is split-adjusted only.

    Returns
    -------
    DataFrame
        DataFrame with adjusted prices.
    """
    # pylint: disable=import-outside-toplevel
    from numpy import zeros

    df = df.copy()
    adj_column = "adj_" + column

    # Reverse the DataFrame order, sorting by date in descending order
    df.sort_index(ascending=False, inplace=True)

    price_col = df[column]
    split_col = df["volume_factor"] if column == "volume" else df["split_factor"]
    dividend_col = df["dividend"] if dividends else zeros(len(price_col))
    adj_price_col = zeros(len(df.index))
    adj_price_col[0] = price_col.iloc[0]

    for i in range(1, len(price_col)):
        adj_price_col[i] = adj_price_col[i - 1] + adj_price_col[i - 1] * (
            (
                (price_col.iloc[i] * split_col.iloc[i - 1])
                - price_col.iloc[i - 1]
                - dividend_col[i - 1]
            )
            / price_col.iloc[i - 1]
        )
    df[adj_column] = adj_price_col

    # Change the DataFrame order back to dates ascending
    df.sort_index(ascending=True, inplace=True)
    return df
