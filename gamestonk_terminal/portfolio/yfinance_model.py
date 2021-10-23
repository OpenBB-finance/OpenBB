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
    return yf.download(tickers=tickers, period="5y", interval="1d", progress=False)


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
        df = tick.dividends.to_frame(name=f"{ticker}_div")
        dfs.append(df)
    return pd.concat(dfs)
