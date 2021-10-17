"""Yfinance model"""
__docformat__ = "numpy"

import yfinance as yf


def get_history(ticker, period, interval):
    """Return raw stock data [Source: Yahoo Finance]

    Parameters
    ----------
    ticker : str
        Ticker to display data for
    period : str
        Period to show information for
    interval : str
        Format of export file

    Returns
    ----------
    history : pd.Dataframe
        History for a stock
    """
    tick = yf.Ticker(ticker)
    return tick.history(period=period, interval=interval)
