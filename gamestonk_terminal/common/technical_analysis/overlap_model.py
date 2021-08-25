"""Overlap Technical Analysis"""
___docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta


def ema(
    s_interval: str, df_stock: pd.DataFrame, length: int, offset: int
) -> pd.DataFrame:
    """Gets exponential moving average (EMA) for stock

    Parameters
    ----------
    s_interval: str
        Data interval
    df_stock: pd.DataFrame
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
    # Daily
    if s_interval == "1440min":
        df_ta = ta.ema(df_stock["Adj Close"], length=length, offset=offset).dropna()

    # Intraday
    else:
        df_ta = ta.ema(df_stock["Close"], length=length, offset=offset).dropna()

    return pd.DataFrame(df_ta)


def sma(
    s_interval: str, df_stock: pd.DataFrame, length: int, offset: int
) -> pd.DataFrame:
    """Gets simple moving average (EMA) for stock

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
        Dataframe containing prices and SMA
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.sma(df_stock["Adj Close"], length=length, offset=offset).dropna()

    # Intraday
    else:
        df_ta = ta.sma(df_stock["Close"], length=length, offset=offset).dropna()

    return pd.DataFrame(df_ta)


def wma(
    s_interval: str, df_stock: pd.DataFrame, length: int, offset: int
) -> pd.DataFrame:
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
    # Daily
    if s_interval == "1440min":
        df_ta = ta.wma(df_stock["Adj Close"], length=length, offset=offset).dropna()

    # Intraday
    else:
        df_ta = ta.wma(df_stock["Close"], length=length, offset=offset).dropna()

    return pd.DataFrame(df_ta)


def hma(
    s_interval: str, df_stock: pd.DataFrame, length: int, offset: int
) -> pd.DataFrame:
    """Gets hull moving average (HMA) for stock

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
        Dataframe containing prices and HMA
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.hma(df_stock["Adj Close"], length=length, offset=offset).dropna()

    # Intraday
    else:
        df_ta = ta.hma(df_stock["Close"], length=length, offset=offset).dropna()

    return pd.DataFrame(df_ta)


def zlma(
    s_interval: str, df_stock: pd.DataFrame, length: int, offset: int
) -> pd.DataFrame:
    """Gets zero-lagged exponential moving average (ZLEMA) for stock

    Parameters
    ----------
    s_interval: str
        Data interval
    df_stock: pd.DataFrame
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
    # Daily
    if s_interval == "1440min":
        df_ta = ta.zlma(df_stock["Adj Close"], length=length, offset=offset).dropna()

    # Intraday
    else:
        df_ta = ta.zlma(df_stock["Close"], length=length, offset=offset).dropna()

    return pd.DataFrame(df_ta)


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
