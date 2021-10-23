"""Yfinance model"""
__docformat__ = "numpy"

from typing import List

import yfinance as yf
import pandas as pd


def get_stocks(tickers: List[str]) -> pd.DataFrame:
    """Gets historic data for list of tickers

    Parameters
    ----------
    tickers : List[str]
        Tickers to get data for

    Returns
    ----------
    data : pd.DataFrame
        Historic daily prices for stocks
    """

    df = yf.download(tickers=tickers, period="5y", interval="1d", progress=False)
    df = df["Adj Close"]
    df.columns = df.columns.str.lower()
    arrays = [["Close" for _ in df.columns], [x.lower() for x in df.columns]]
    tuples = list(zip(*arrays))
    headers = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
    df.columns = headers
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
