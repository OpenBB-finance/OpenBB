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
        Historic daily prices for a stock
    """
    return yf.download(tickers=tickers, period="5y", interval="1d")
