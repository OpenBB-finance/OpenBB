"""Momentum Technical Analysis"""
__docformat__ = "numpy"

import logging
from typing import Tuple

import numpy as np
import pandas as pd
import pandas_ta as ta
from sklearn.linear_model import LinearRegression

from openbb_terminal.rich_config import console
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def cci(
    high_vals: pd.Series,
    low_vals: pd.Series,
    close_vals: pd.Series,
    window: int = 14,
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
    window: int
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
            length=window,
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
def rsi(
    values: pd.Series, window: int = 14, scalar: float = 100, drift: int = 1
) -> pd.DataFrame:
    """Relative strength index

    Parameters
    ----------
    values: pd.Series
        Dataframe of prices
    window: int
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
        ta.rsi(values, length=window, scalar=scalar, drift=drift).dropna()
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
def fisher(high_vals: pd.Series, low_vals: pd.Series, window: int = 14) -> pd.DataFrame:
    """Fisher Transform

    Parameters
    ----------
    high_vals: pd.Series
        High values
    low_vals: pd.Series
        Low values
    window: int
        Length for indicator window
    Returns
    ----------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    return pd.DataFrame(ta.fisher(high=high_vals, low=low_vals, length=window).dropna())


@log_start_end(log=logger)
def cg(values: pd.Series, window: int) -> pd.DataFrame:
    """Center of gravity

    Parameters
    ----------
    values: pd.DataFrame
        Data to use with close being titled values
    window: int
        Length for indicator window
    Returns
    ----------
    d.DataFrame
        Dataframe of technical indicator
    """
    return pd.DataFrame(ta.cg(close=values, length=window).dropna())


@log_start_end(log=logger)
def clenow_momentum(
    values: pd.Series, window: int = 90
) -> Tuple[float, float, pd.Series]:
    """Gets the Clenow Volatility Adjusted Momentum.  this is defined as the regression coefficient on log prices
    multiplied by the R^2 value of the regression

    Parameters
    ----------
    values: pd.Series
        Values to perform regression for
    window: int
        Length of lookback period

    Returns
    -------
    float:
        R2 of fit to log data
    float:
        Coefficient of linear regression
    pd.Series:
        Values for best fit line
    """
    if len(values) < window:
        console.print(
            f"[red]Calculation asks for at least last {window} days of data[/red]"
        )
        return np.nan, np.nan, pd.Series()

    values = values[-window:]

    y = np.log(values)
    X = np.arange(len(y)).reshape(-1, 1)

    lr = LinearRegression()
    lr.fit(X, y)

    r2 = lr.score(X, y)
    coef = lr.coef_[0]

    return r2, coef, pd.Series(lr.predict(X))
