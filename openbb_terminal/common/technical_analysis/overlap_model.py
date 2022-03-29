"""Overlap Technical Analysis"""
___docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

WINDOW_LENGTHS = [20, 50]
WINDOW_LENGTHS2 = [10, 20]


@log_start_end(log=logger)
def ema(values: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets exponential moving average (EMA) for stock

    Parameters
    ----------
    values: pd.DataFrame
        Dataframe of dates and prices
    length: int
        Length of EMA window
    offset: int
        Length of offset

    Returns
    ----------
    pd.DataFrame
        Dataframe containing prices and EMA
    """
    return pd.DataFrame(ta.ema(values, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def sma(values: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets simple moving average (EMA) for stock

     Parameters
     ----------
     values: pd.DataFrame
         Dataframe of dates and prices
     length: int
         Length of SMA window
     offset: int
         Length of offset

     Returns
     ----------
    pd.DataFrame
         Dataframe containing prices and SMA
    """
    return pd.DataFrame(ta.sma(values, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def wma(values: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets weighted moving average (WMA) for stock

    Parameters
    ----------
    values: pd.DataFrame
        Dataframe of dates and prices
    length: int
        Length of SMA window
    offset: int
        Length of offset

    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe containing prices and WMA
    """
    return pd.DataFrame(ta.wma(values, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def hma(values: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets hull moving average (HMA) for stock

    Parameters
    ----------
    values: pd.DataFrame
        Dataframe of dates and prices
    length: int
        Length of SMA window
    offset: int
        Length of offset

    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe containing prices and HMA
    """
    return pd.DataFrame(ta.hma(values, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def zlma(values: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets zero-lagged exponential moving average (ZLEMA) for stock

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of dates and prices
    length: int
        Length of EMA window
    offset: int
        Length of offset

    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe containing prices and EMA
    """
    return pd.DataFrame(ta.zlma(values, length=length, offset=offset)).dropna()


@log_start_end(log=logger)
def vwap(day_df: pd.DataFrame, offset: int) -> pd.DataFrame:
    """Gets volume weighted average price (VWAP)

    Parameters
    ----------
    day_df: pd.DataFrame
        Dataframe of dates and prices for the last trading day
    offset: int
        Length of offset
    Returns
    ----------
    df_vwap: pd.DataFrame
        Dataframe with VWAP data
    """

    df_vwap = ta.vwap(
        high=day_df["High"],
        low=day_df["Low"],
        close=day_df["Close"],
        volume=day_df["Volume"],
        offset=offset,
    )

    return pd.DataFrame(df_vwap)
