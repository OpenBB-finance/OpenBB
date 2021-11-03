"""Yfinance model"""
__docformat__ = "numpy"

from typing import List
from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd


def get_stocks(tickers: List[str], start: datetime) -> pd.DataFrame:
    """Gets historic data for list of tickers

    Parameters
    ----------
    tickers : List[str]
        Tickers to get data for
    start : datetime
        First date in stock filtered dataframe

    Returns
    ----------
    data : pd.DataFrame
        Historic daily prices for stocks
    """
    df = yf.download(
        tickers=tickers,
        start=start - timedelta(days=365),
        interval="1d",
        progress=False,
    )
    df = df["Adj Close"]
    if len(tickers) > 1:
        df.columns = df.columns.str.lower()
        arrays = [["Close" for _ in df.columns], [x.lower() for x in df.columns]]
        tuples = list(zip(*arrays))
        headers = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
        df.columns = headers
    if len(tickers) == 1:
        df = df.to_frame(name=("Close", tickers[0]))
    return df


def get_dividends(tickers: List[str]) -> pd.DataFrame:
    """Past dividends for list of tickers

    Parameters
    ----------
    tickers : List[str]
        Tickers to get data for

    Returns
    ----------
    data : pd.DataFrame
        Historic dividends for stocks
    """
    dfs = []
    for ticker in tickers:
        tick = yf.Ticker(ticker)
        df = tick.dividends.to_frame(name=("Dividend", ticker))
        dfs.append(df)
    return pd.concat(dfs)


def get_market(start: datetime, ticker: str = "SPY") -> pd.DataFrame:
    """Get historical data for market asset

    Parameters
    ----------
    ticker : str
        Ticker to get data for
    start : datetime
        First date in stock filtered dataframe

    Returns
    ----------
    data : pd.DataFrame
        Historic prices for SPY
    """
    tick = yf.Ticker(ticker)
    df = tick.history(
        start=start - timedelta(days=365),
        interval="1d",
    )["Close"]
    return df.to_frame(name=("Market", "Close"))
