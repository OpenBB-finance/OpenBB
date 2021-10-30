"""Portfolio Helper"""
__docformat__ = "numpy"

import yfinance as yf


def is_ticker(ticker: str) -> bool:
    """Determine whether a string is a valid ticker

    Parameters
    ----------
    ticker : str
        The string to be tested

    Returns
    ----------
    answer : bool
        Whether the string is a ticker
    """
    item = yf.Ticker(ticker)
    return "previousClose" in item.info
