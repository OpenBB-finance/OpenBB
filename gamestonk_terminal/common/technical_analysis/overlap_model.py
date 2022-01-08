"""Overlap Technical Analysis"""
___docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta

WINDOW_LENGTHS = [20, 50]
WINDOW_LENGTHS2 = [10, 20]


def ema(data: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets exponential moving average (EMA) for stock

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
    pd.DataFrame
        Dataframe containing prices and EMA
    """
    return pd.DataFrame(ta.ema(data["values"], length=length, offset=offset).dropna())


def sma(data: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets simple moving average (EMA) for stock

     Parameters
     ----------
     data: pd.DataFrame
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
    return pd.DataFrame(ta.sma(data["values"], length=length, offset=offset).dropna())


def wma(data: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets weighted moving average (WMA) for stock

    Parameters
    ----------
    s_interval: str
        Data interval
    df_stock: pd.DataFrame
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
    return pd.DataFrame(ta.wma(data["values"], length=length, offset=offset).dropna())


def hma(data: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
    """Gets hull moving average (HMA) for stock

    Parameters
    ----------
    data: pd.DataFrame
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
    return pd.DataFrame(ta.hma(data["values"], length=length, offset=offset).dropna())


def zlma(data: pd.DataFrame, length: int, offset: int) -> pd.DataFrame:
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
    return pd.DataFrame(ta.zlma(data["values"], length=length, offset=offset).dropna())


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
