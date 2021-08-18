"""Momentum Technical Analysis"""
__docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta


def cci(
    s_interval: str, df_stock: pd.DataFrame, length: int, scalar: float
) -> pd.DataFrame:
    """Commodity channel index

    Parameters
    ----------
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    length: int
        Length of window
    scalar: float
        Scalar variable

    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.cci(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Adj Close"],
            length=length,
            scalar=scalar,
        ).dropna()

    # Intraday
    else:
        df_ta = ta.cci(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            length=length,
            scalar=scalar,
        ).dropna()

    return pd.DataFrame(df_ta)


def macd(
    s_interval: str, df_stock: pd.DataFrame, n_fast: int, n_slow: int, n_signal: int
) -> pd.DataFrame:
    """Moving average convergence divergence

    Parameters
    ----------
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.macd(
            df_stock["Adj Close"], fast=n_fast, slow=n_slow, signal=n_signal
        ).dropna()

    # Intraday
    else:
        df_ta = ta.macd(
            df_stock["Close"], fast=n_fast, slow=n_slow, signal=n_signal
        ).dropna()

    return pd.DataFrame(df_ta)


def rsi(
    s_interval: str, df_stock: pd.DataFrame, length: int, scalar: float, drift: int
) -> pd.DataFrame:
    """Relative strength index

    Parameters
    ----------
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    length: int
        Length of window
    scalar: float
        Scalar variable
    drift: int
        Drift variable

    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.rsi(
            df_stock["Adj Close"], length=length, scalar=scalar, drift=drift
        ).dropna()

    # Intraday
    else:
        df_ta = ta.rsi(
            df_stock["Close"], length=length, scalar=scalar, drift=drift
        ).dropna()
    return pd.DataFrame(df_ta)


def stoch(
    s_interval: str,
    df_stock: pd.DataFrame,
    fastkperiod: int,
    slowdperiod: int,
    slowkperiod: int,
):
    """Stochastic oscillator

    Parameters
    ----------
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.stoch(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Adj Close"],
            k=fastkperiod,
            d=slowdperiod,
            smooth_k=slowkperiod,
        ).dropna()

    # Intraday
    else:
        df_ta = ta.stoch(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            k=fastkperiod,
            d=slowdperiod,
            smooth_k=slowkperiod,
        ).dropna()

    return pd.DataFrame(df_ta)


def fisher(s_interval: str, df_stock: pd.DataFrame, length: int) -> pd.DataFrame:
    """Fisher Transform

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.fisher(
            high=df_stock["High"], low=df_stock["Low"], length=length
        ).dropna()

    # Intraday
    else:
        df_ta = ta.fisher(
            high=df_stock["High"], low=df_stock["Low"], length=length
        ).dropna()

    return pd.DataFrame(df_ta)


def cg(s_interval: str, df_stock: pd.DataFrame, length: int) -> pd.DataFrame:
    """Center of gravity

    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_interval: str
        Stock time interval
    df_stock: pd.DataFrame
        Dataframe of prices
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.cg(close=df_stock["Adj Close"], length=length).dropna()

    # Intraday
    else:
        df_ta = ta.cg(close=df_stock["Close"], length=length).dropna()

    return pd.DataFrame(df_ta)
