"""Alpha Vantage Helpers Module."""

import re
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd

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


def calculate_adjusted_prices(df: pd.DataFrame, column: str, dividends: bool = False):
    """Calculate the split-adjusted prices, or split and dividend adjusted prices.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame with unadjusted OHLCV values + split_factor + dividend
    column: str
        The column name to adjust.
    dividends: bool
        Whether to adjust for both splits and dividends. Default is split-adjusted only.

    Returns
    -------
    pd.DataFrame
        DataFrame with adjusted prices.
    """
    df = df.copy()
    adj_column = "adj_" + column

    # Reverse the DataFrame order, sorting by date in descending order
    df.sort_index(ascending=False, inplace=True)

    price_col = df[column].values
    split_col = df["volume_factor"] if column == "volume" else df["split_factor"].values
    dividend_col = df["dividend"].values if dividends else np.zeros(len(price_col))
    adj_price_col = np.zeros(len(df.index))
    adj_price_col[0] = price_col[0]

    for i in range(1, len(price_col)):
        adj_price_col[i] = adj_price_col[i - 1] + adj_price_col[i - 1] * (
            ((price_col[i] * split_col[i - 1]) - price_col[i - 1] - dividend_col[i - 1])
            / price_col[i - 1]
        )
    df[adj_column] = adj_price_col

    # Change the DataFrame order back to dates ascending
    df.sort_index(ascending=True, inplace=True)
    return df
