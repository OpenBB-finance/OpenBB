"""Momentum Technical Analysis"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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
    high_vals: pd.Series
        High values
    low_values: pd.Series
        Low values
    close-values: pd.Series
        Close values
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


@log_start_end(log=logger)
def macd(
    values: pd.DataFrame,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
) -> pd.DataFrame:
    """Moving average convergence divergence

    Parameters
    ----------
    values: pd.Series
        Values for calculation
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
        ta.macd(values, fast=n_fast, slow=n_slow, signal=n_signal).dropna()
    )


@log_start_end(log=logger)
def rsi(values: pd.Series, length: int, scalar: float, drift: int) -> pd.DataFrame:
    """Relative strength index

    Parameters
    ----------
    values: pd.Series
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
        ta.rsi(values, length=length, scalar=scalar, drift=drift).dropna()
    )


@log_start_end(log=logger)
def stoch(
    high_vals: pd.Series,
    low_vals: pd.Series,
    close_vals: pd.Series,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
):
    """Stochastic oscillator

    Parameters
    ----------
    high_vals: pd.Series
        High values
    low_vals: pd.Series
        Low values
    close-vals: pd.Series
        Close values
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
            high=high_vals,
            low=low_vals,
            close=close_vals,
            k=fastkperiod,
            d=slowdperiod,
            smooth_k=slowkperiod,
        ).dropna()
    )


@log_start_end(log=logger)
def fisher(high_vals: pd.Series, low_vals: pd.Series, length: int = 14) -> pd.DataFrame:
    """Fisher Transform

    Parameters
    ----------
    high_vals: pd.Series
        High values
    low_vals: pd.Series
        Low values
    length: int
        Length for indicator window
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    return pd.DataFrame(ta.fisher(high=high_vals, low=low_vals, length=length).dropna())


@log_start_end(log=logger)
def cg(values: pd.Series, length: int) -> pd.DataFrame:
    """Center of gravity

    Parameters
    ----------
    values: pd.DataFrame
        Data to use with close being titled values
    length: int
        Length for indicator window
    Returns
    ----------
    d.DataFrame
        Dataframe of technical indicator
    """
    return pd.DataFrame(ta.cg(close=values, length=length).dropna())
