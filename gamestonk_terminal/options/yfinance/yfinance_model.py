"""Yfinance options model"""
__docformat__ = "numpy"

from typing import List
import yfinance as yf
import pandas as pd

def option_expirations(ticker:str):
    """Get avaialable expiration dates for given ticker

    Parameters
    ----------
    ticker: str
        Ticker to get expirations for

    Returns
    -------
    dates: List[str]
        List of of available expirations
    """
    yfticker = yf.Ticker(ticker)
    dates = list(yfticker.options)
    return dates