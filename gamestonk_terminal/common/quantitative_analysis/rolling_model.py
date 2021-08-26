"""Rolling Statistics"""
__docformat__ = "numpy"

from typing import Tuple

import pandas as pd
import pandas_ta as ta


def get_rolling_avg(
    df_stock: pd.DataFrame, length: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return rolling mean and standard deviation

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    length : int
        Length of rolling window

    Returns
    -------
    pd.DataFrame :
        Dataframe of rolling mean
    pd.DataFrame :
        Dataframe of rolling standard deviation
    """
    df_stock = df_stock["Adj Close"]

    rolling_mean = df_stock.rolling(length, center=True, min_periods=1).mean()
    rolling_std = df_stock.rolling(length, center=True, min_periods=1).std()

    return pd.DataFrame(rolling_mean), pd.DataFrame(rolling_std)


def get_spread(
    s_interval: str, df_stock: pd.DataFrame, length: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Standard Deviation and Variance

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        DataFrame of prices

    Returns
    -------
    df_sd : pd.DataFrame
        Dataframe of rolling standard deviation
    df_var : pd.DataFrame
        Dataframe of rolling standard deviation
    """
    # Daily
    if s_interval == "1440min":
        df_sd = ta.stdev(
            close=df_stock["Adj Close"],
            length=length,
        ).dropna()
        df_var = ta.variance(
            close=df_stock["Adj Close"],
            length=length,
        ).dropna()

    # Intraday
    else:
        df_sd = ta.stdev(
            close=df_stock["Close"],
            length=length,
        ).dropna()
        df_var = ta.variance(
            close=df_stock["Adj Close"],
            length=length,
        ).dropna()

    return pd.DataFrame(df_sd), pd.DataFrame(df_var)


def get_quantile(
    s_interval: str, df_stock: pd.DataFrame, length: int, quantile_pct: float
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Overlay Median & Quantile

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        Dataframe of prices
    length : int
        Length of window
    quantile : float
        Quantile to display

    Returns
    -------
    df_med : pd.DataFrame
        Dataframe of median prices over window
    df_quantile : pd.DataFrame
        Dataframe of gievn quantile prices over window
    """
    if s_interval == "1440min":
        df_med = ta.median(close=df_stock["Adj Close"], length=length).dropna()
        df_quantile = ta.quantile(
            df_stock["Adj Close"],
            length=length,
            q=quantile_pct,
        ).dropna()
    else:
        df_med = ta.median(close=df_stock["Adj Close"], length=length).dropna()
        df_quantile = ta.quantile(
            df_stock["Close"],
            length=length,
            q=quantile_pct,
        ).dropna()

    return pd.DataFrame(df_med), pd.DataFrame(df_quantile)


def get_skew(s_interval: str, df_stock: pd.DataFrame, length: int) -> pd.DataFrame:
    """Skewness Indicator

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        Dataframe of prices
    length : int
        Length of window

    Returns
    -------
    df_skew : pd.DataFrame
        Dataframe of rolling skew
    """
    # Daily
    if s_interval == "1440min":
        df_skew = ta.skew(close=df_stock["Adj Close"], length=length).dropna()
    # Intraday
    else:
        df_skew = ta.skew(close=df_stock["Close"], length=length).dropna()

    return df_skew
