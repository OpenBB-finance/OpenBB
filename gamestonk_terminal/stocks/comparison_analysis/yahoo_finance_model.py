"""Yahoo Finance Comparison Model"""
__docformat__ = "numpy"

from datetime import datetime, timedelta
from typing import List

import pandas as pd
import yfinance as yf

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
}


def get_historical(
    ticker: str,
    similar_tickers: List[str],
    start: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    candle_type: str = "a",
) -> pd.DataFrame:
    """Get historical prices for all comparison stocks

    Parameters
    ----------
    ticker : str
        Base ticker
    similar_tickers : List[str]
        List of similar tickers
    start : str, optional
        Start date of comparison.  Defaults to 1 year previously
    candle_type : str, optional
        Candle variable to compare, by default "a" for Adjusted Close

    Returns
    -------
    pd.DataFrame
        Dataframe containing candle type variable for each ticker
    """
    all_tickers = [ticker, *similar_tickers]
    # To avoid having to recursively append, just do a single yfinance call.  This will give dataframe
    # where all tickers are columns.
    return yf.download(all_tickers, start=start, progress=False, threads=False)[
        d_candle_types[candle_type]
    ].dropna(axis=1)


def get_1y_sp500() -> pd.DataFrame:
    """
    Gets the last year of Adj Close prices for all current SP 500 stocks.
    They are scraped daily using yfinance at https://github.com/jmaslek/daily_sp_500

    Returns
    -------
    pd.DataFrame
        DataFrame containing last 1 year of closes for all SP500 stocks.
    """
    return pd.read_csv(
        "https://raw.githubusercontent.com/jmaslek/daily_sp_500/main/SP500_prices_1yr.csv",
        index_col=0,
    )
