"""Custom Indicator Models"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple

import pandas as pd

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def calculate_fib_levels(
    df_stock: pd.DataFrame,
    period: int = 120,
    open_date: Any = None,
    close_date: Any = None,
) -> Tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp, float, float]:
    """Calculate Fibonacci levels

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    period : int
        Days to look back for retracement
    open_date : Any
        Custom start date for retracement
    close_date : Any
        Custom end date for retracement

    Returns
    -------
    df : pd.DataFrame
        Dataframe of fib levels
    min_date: pd.Timestamp
        Date of min point
    max_date: pd.Timestamp:
        Date of max point
    min_pr: float
        Price at min point
    max_pr: float
        Price at max point
    """
    if open_date and close_date:
        if open_date not in df_stock.index:
            date0 = df_stock.index[df_stock.index.get_loc(open_date, method="nearest")]
            console.print(f"Start date not in df_stock.  Using nearest: {date0}")
        else:
            date0 = open_date
        if close_date not in df_stock.index:
            date1 = df_stock.index[df_stock.index.get_loc(close_date, method="nearest")]
            console.print(f"End date not in df_stock.  Using nearest: {date1}")
        else:
            date1 = close_date

        df_stock0 = df_stock.loc[date0, "Adj Close"]
        df_stock1 = df_stock.loc[date1, "Adj Close"]

        min_pr = min(df_stock0, df_stock1)
        max_pr = max(df_stock0, df_stock1)

        if min_pr == df_stock0:
            min_date = date0
            max_date = date1
        else:
            min_date = date1
            max_date = date0
    else:
        data_to_use = df_stock.iloc[period:]["Adj Close"]

        min_pr = data_to_use.min()
        min_date = data_to_use.idxmin()
        max_pr = data_to_use.max()
        max_date = data_to_use.idxmax()

    fib_levels = [0, 0.235, 0.382, 0.5, 0.618, 1]
    price_dif = max_pr - min_pr

    levels = [round(max_pr - price_dif * f_lev, 2) for f_lev in fib_levels]

    df = pd.DataFrame()
    df["Level"] = fib_levels
    df["Level"] = df["Level"].apply(lambda x: str(x * 100) + "%")
    df["Price"] = levels

    return df, min_date, max_date, min_pr, max_pr
