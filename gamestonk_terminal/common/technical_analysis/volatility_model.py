"""Volatility Technical Indicators"""
__docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta

MAMODES = ["ema", "sma", "wma", "hma", "zlma"]


def bbands(
    s_interval: str, df_stock: pd.DataFrame, length: int, n_std: float, mamode: str
) -> pd.DataFrame:
    """Calculate Bollinger Bands

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        DataFrame of stock data
    length : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average

    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe of bollinger band data
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.bbands(
            close=df_stock["Adj Close"],
            length=length,
            std=n_std,
            mamode=mamode,
        ).dropna()

    # Intraday
    else:
        df_ta = ta.bbands(
            close=df_stock["Close"],
            length=length,
            std=n_std,
            mamode=mamode,
        ).dropna()

    return df_ta


def donchian(
    df_stock: pd.DataFrame,
    upper_length: int,
    lower_length: int,
) -> pd.DataFrame:
    """Calculate Donchian Channels

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        DataFrame of stock data
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel


    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe of upper and lower channels
    """
    df_ta = ta.donchian(
        high=df_stock["High"],
        low=df_stock["Low"],
        upper_length=upper_length,
        lower_length=lower_length,
    ).dropna()

    return df_ta


def kc(
    s_interval: str,
    df_stock: pd.DataFrame,
    length: int,
    scalar: float,
    mamode: str,
    offset: int,
) -> pd.DataFrame:
    """Keltner Channels

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        Dataframe of prices
    length : int
        Length of window
    mamode: str
        Type of filter
    offset : int
        Offset value

    Returns
    -------
    df_en : pd.DataFrame
        Dataframe of rolling kc
    """
    # Daily
    if s_interval == "1440min":
        df_kc = ta.kc(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Adj Close"],
            length=length,
            scalar=scalar,
            mamode=mamode,
            offset=offset,
        ).dropna()

    # Intraday
    else:
        df_kc = ta.kc(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            length=length,
            scalar=scalar,
            mamode=mamode,
            offset=offset,
        ).dropna()

    return df_kc
