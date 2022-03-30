"""Yfinance options model"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas as pd
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def option_expirations(ticker: str):
    """Get available expiration dates for given ticker

    Parameters
    ----------
    ticker: str
        Ticker to get expirations for

    Returns
    -------
    dates: List[str]
        List of of available expirations
    """
    yf_ticker = yf.Ticker(ticker)
    dates = list(yf_ticker.options)
    if not dates:
        console.print("No expiration dates found for ticker. \n")
    return dates


@log_start_end(log=logger)
def get_option_chain(ticker: str, expiration: str) -> pd.DataFrame:
    """Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    ticker: str
        Ticker to get options for
    expiration: str
        Date to get options for

    Returns
    -------
    chains: yf.ticker.Options
        Options chain
    """
    yf_ticker = yf.Ticker(ticker)
    chains = yf_ticker.option_chain(expiration)
    return chains


@log_start_end(log=logger)
def get_dividend(ticker: str) -> pd.Series:
    """Gets option chain from yf for given ticker and expiration

    Parameters
    ----------
    ticker: str
        Ticker to get options for

    Returns
    -------
    chains: yf.ticker.Dividends
        Dividends
    """
    yf_ticker = yf.Ticker(ticker)
    dividend = yf_ticker.dividends
    return dividend


@log_start_end(log=logger)
def get_x_values(current_price: float, options: List[Dict[str, int]]) -> List[float]:
    """Generates different price values that need to be tested"""
    x_list = list(range(101))
    mini = current_price
    maxi = current_price
    if len(options) == 0:
        mini *= 0.5
        maxi *= 1.5
    elif len(options) > 0:
        biggest = max(options, key=lambda x: x["strike"])
        smallest = min(options, key=lambda x: x["strike"])
        maxi = max(maxi, biggest["strike"]) * 1.2
        mini = min(mini, smallest["strike"]) * 0.8
    num_range = maxi - mini
    return [(x / 100) * num_range + mini for x in x_list]


def get_y_values(
    base: float,
    price: float,
    options: List[Dict[Any, Any]],
    underlying: int,
) -> float:
    """Generates y values for corresponding x values"""
    option_change = 0
    change = price - base
    for option in options:
        if option["type"] == "call":
            abs_change = price - option["strike"] if price > option["strike"] else 0
            option_change += option["sign"] * abs_change
        elif option["type"] == "put":
            abs_change = option["strike"] - price if price < option["strike"] else 0
            option_change += option["sign"] * abs_change
    return (change * underlying) + option_change


@log_start_end(log=logger)
def generate_data(
    current_price: float, options: List[Dict[str, int]], underlying: int
) -> Tuple[List[float], List[float], List[float]]:
    """Gets x values, and y values before and after premiums"""
    x_vals = get_x_values(current_price, options)
    base = current_price
    total_cost = sum(x["cost"] for x in options)
    before = [get_y_values(base, x, options, underlying) for x in x_vals]
    if total_cost != 0:
        after = [
            get_y_values(base, x, options, underlying) - total_cost for x in x_vals
        ]
        return x_vals, before, after
    return x_vals, before, []


@log_start_end(log=logger)
def get_price(ticker: str) -> float:
    """Get current price for a given ticker

    Parameters
    ----------
    ticker : str
        The ticker to get the price for

    Returns
    ----------
    price : float
        The price of the ticker
    """
    ticker_yahoo = yf.Ticker(ticker)
    data = ticker_yahoo.history()
    last_quote = data.tail(1)["Close"].iloc[0]
    return last_quote


@log_start_end(log=logger)
def get_info(ticker: str):
    """Get info for a given ticker

    Parameters
    ----------
    ticker : str
        The ticker to get the price for

    Returns
    ----------
    price : float
        The info for a given ticker
    """
    tick = yf.Ticker(ticker)
    return tick.info


@log_start_end(log=logger)
def get_closing(ticker: str) -> pd.Series:
    """Get closing prices for a given ticker

    Parameters
    ----------
    ticker : str
        The ticker to get the price for

    Returns
    ----------
    price : List[float]
        A list of closing prices for a ticker
    """
    tick = yf.Ticker(ticker)
    return tick.history(period="1y")["Close"]


@log_start_end(log=logger)
def get_dte(date: str) -> int:
    """Gets days to expiration from yfinance option date"""
    return (datetime.strptime(date, "%Y-%m-%d") - datetime.now()).days


@log_start_end(log=logger)
def get_iv_surface(ticker: str) -> pd.DataFrame:
    """Gets IV surface for calls and puts for ticker

    Parameters
    ----------
    ticker: str
        Stock ticker to get

    Returns
    -------
    pd.DataFrame
        Dataframe of DTE, Strike and IV
    """

    stock = yf.Ticker(ticker)
    dates = stock.options
    vol_df = pd.DataFrame()
    columns = ["strike", "impliedVolatility", "openInterest", "lastPrice"]
    for date in dates:
        df = stock.option_chain(date).calls[columns]
        df["dte"] = get_dte(date)
        vol_df = pd.concat([vol_df, df], axis=0)
        df = stock.option_chain(date).puts[columns]
        df["dte"] = get_dte(date)
        vol_df = pd.concat([vol_df, df], axis=0)
    return vol_df
