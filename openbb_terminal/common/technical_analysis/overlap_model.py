"""Overlap Technical Analysis"""
___docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

WINDOW_LENGTHS = [20, 50]
WINDOW_LENGTHS2 = [10, 20]


@log_start_end(log=logger)
def ema(data: pd.Series, length: int = 50, offset: int = 0) -> pd.DataFrame:
    """Gets exponential moving average (EMA) for stock

    Parameters
    ----------
    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of EMA window
    offset: int
        Length of offset

    Returns
    -------
    pd.DataFrame
        Dataframe containing prices and EMA
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a DataFrame.[/red]\n")
        return pd.DataFrame()
    return pd.DataFrame(ta.ema(data, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def sma(data: pd.Series, length: int = 50, offset: int = 0) -> pd.DataFrame:
    """Gets simple moving average (SMA) for stock

    Parameters
    ----------
    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of SMA window
    offset: int
        Length of offset

    Returns
    -------
    pd.DataFrame
        Dataframe containing prices and SMA
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a DataFrame.[/red]\n")
        return pd.DataFrame()
    return pd.DataFrame(ta.sma(data, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def wma(data: pd.Series, length: int = 50, offset: int = 0) -> pd.DataFrame:
    """Gets weighted moving average (WMA) for stock

    Parameters
    ----------
    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of SMA window
    offset: int
        Length of offset

    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe containing prices and WMA
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a DataFrame.[/red]\n")
        return pd.DataFrame()
    return pd.DataFrame(ta.wma(data, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def hma(data: pd.Series, length: int = 50, offset: int = 0) -> pd.DataFrame:
    """Gets hull moving average (HMA) for stock

    Parameters
    ----------
    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of SMA window
    offset: int
        Length of offset

    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe containing prices and HMA
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a DataFrame.[/red]\n")
        return pd.DataFrame()
    return pd.DataFrame(ta.hma(data, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def zlma(data: pd.Series, length: int = 50, offset: int = 0) -> pd.DataFrame:
    """Gets zero-lagged exponential moving average (ZLEMA) for stock

    Parameters
    ----------
    data: pd.Series
        Dataframe of dates and prices
    length: int
        Length of EMA window
    offset: int
        Length of offset

    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe containing prices and EMA
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a DataFrame.[/red]\n")
        return pd.DataFrame()
    return pd.DataFrame(ta.zlma(data, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def vwap(data: pd.DataFrame, offset: int = 0) -> pd.DataFrame:
    """Gets volume weighted average price (VWAP)

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of dates and prices
    offset: int
        Length of offset
    Returns
    -------
    df_vwap: pd.DataFrame
        Dataframe with VWAP data
    """

    df_vwap = ta.vwap(
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        volume=data["Volume"],
        offset=offset,
    )

    return pd.DataFrame(df_vwap)
