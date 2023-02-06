"""Yfinance model"""
__docformat__ = "numpy"

import difflib
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import yfinance as yf

from openbb_terminal.stocks.sector_industry_analysis import financedatabase_model


def get_stocks(symbols: List[str], start: datetime) -> pd.DataFrame:
    """Gets historic data for list of tickers

    Parameters
    ----------
    symbols : List[str]
        Tickers to get data for
    start : datetime
        First date in stock filtered dataframe

    Returns
    -------
    data : pd.DataFrame
        Historic daily prices for stocks
    """
    df = yf.download(
        tickers=symbols,
        start=start - timedelta(days=365),
        interval="1d",
        progress=False,
    )
    df = df["Adj Close"]
    if len(symbols) > 1:
        df.columns = df.columns.str.lower()
        arrays = [["Close" for _ in df.columns], [x.lower() for x in df.columns]]
        tuples = list(zip(*arrays))
        headers = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
        df.columns = headers
    if len(symbols) == 1:
        df = df.to_frame(name=("Close", symbols[0]))
    return df


def get_dividends(symbols: List[str]) -> pd.DataFrame:
    """Past dividends for list of tickers

    Parameters
    ----------
    symbols : List[str]
        Tickers to get data for

    Returns
    -------
    data : pd.DataFrame
        Historic dividends for stocks
    """
    dfs = []
    for ticker in symbols:
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
    -------
    data : pd.DataFrame
        Historic prices for SPY
    """
    tick = yf.Ticker(ticker)
    df = tick.history(
        start=start - timedelta(days=365),
        interval="1d",
    )["Close"]
    return df.to_frame(name=("Market", "Close"))


def get_country(ticker):
    country = "NA"
    data = yf.Ticker(ticker).stats()

    if "summaryProfile" in data:
        country = data["summaryProfile"]["country"]
        if country not in financedatabase_model.get_countries():
            similar_cmd = difflib.get_close_matches(
                country,
                financedatabase_model.get_countries(),
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                country = similar_cmd[0]
    return country
