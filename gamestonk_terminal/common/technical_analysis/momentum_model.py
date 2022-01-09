"""Momentum Technical Analysis"""
__docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta


def cci(
    high_vals: pd.Series,
    low_vals: pd.Series,
    close_vals: pd.Series,
    length: int = 14,
    scalar: float = 0.0015,
) -> pd.DataFrame:
    """Commodity channel index

    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of prices.  Needs high Low and Close
    length: int
        Length of window
    scalar: float
        Scalar variable

    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator
    """
    return pd.DataFrame(
        ta.cci(
            high=high_vals,
            low=low_vals,
            close=close_vals,
            length=length,
            scalar=scalar,
        ).dropna()
    )


def macd(
    data: pd.DataFrame,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
) -> pd.DataFrame:
    """Moving average convergence divergence

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of prices
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator
    """
    return pd.DataFrame(
        ta.macd(data["values"], fast=n_fast, slow=n_slow, signal=n_signal).dropna()
    )


def rsi(data: pd.DataFrame, length: int, scalar: float, drift: int) -> pd.DataFrame:
    """Relative strength index

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of prices
    length: int
        Length of window
    scalar: float
        Scalar variable
    drift: int
        Drift variable

    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator
    """
    return pd.DataFrame(
        ta.rsi(data["values"], length=length, scalar=scalar, drift=drift).dropna()
    )


def stoch(
    df_stock: pd.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
):
    """Stochastic oscillator

    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of prices.  Needs High Low and Adj Close
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    Returns
    ----------
    pd.DataFrame
        Dataframe of technical indicator
    """
    return pd.DataFrame(
        ta.stoch(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Adj Close"],
            k=fastkperiod,
            d=slowdperiod,
            smooth_k=slowkperiod,
        ).dropna()
    )


def fisher(df_stock: pd.DataFrame, length: int = 14) -> pd.DataFrame:
    """Fisher Transform

    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of prices.  Needs to contain High and Low
    length: int
        Lengyh for indicator window
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    return pd.DataFrame(
        ta.fisher(high=df_stock["High"], low=df_stock["Low"], length=length).dropna()
    )


def cg(data: pd.DataFrame, length: int) -> pd.DataFrame:
    """Center of gravity

    Parameters
    ----------
    data: pd.DataFrame
        Data to use with close being titled values
    length: int
        Length for indicator window
    Returns
    ----------
    d.DataFrame
        Dataframe of technical indicator
    """
    return pd.DataFrame(ta.cg(close=data["values"], length=length).dropna())
