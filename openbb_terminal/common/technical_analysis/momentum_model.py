"""Momentum Technical Analysis"""
__docformat__ = "numpy"

import logging
from typing import Tuple

import numpy as np
import pandas as pd
import pandas_ta as ta
from sklearn.linear_model import LinearRegression

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def cci(
    data: pd.DataFrame,
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
    -------
    pd.DataFrame
        Dataframe of technical indicator
    """

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.cci(
            high=data["High"],
            low=data["Low"],
            close=data[close_col],
            length=window,
            scalar=scalar,
        ).dropna()
    )


@log_start_end(log=logger)
def macd(
    data: pd.Series,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
) -> pd.DataFrame:
    """Moving average convergence divergence

    Parameters
    ----------
    data: pd.Series
        Values for calculation
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    Returns
    -------
    pd.DataFrame
        Dataframe of technical indicator
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a DataFrame.[/red]\n")
        return pd.DataFrame()
    return pd.DataFrame(
        ta.macd(data, fast=n_fast, slow=n_slow, signal=n_signal).dropna()
    )


@log_start_end(log=logger)
def rsi(
    data: pd.Series, window: int = 14, scalar: float = 100, drift: int = 1
) -> pd.DataFrame:
    """Relative strength index

    Parameters
    ----------
    data: pd.Series
        Dataframe of prices
    window: int
        Length of window
    scalar: float
        Scalar variable
    drift: int
        Drift variable

    Returns
    -------
    pd.DataFrame
        Dataframe of technical indicator
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a DataFrame.[/red]\n")
        return pd.DataFrame()
    raw_data = ta.rsi(data, length=window, scalar=scalar, drift=drift)
    if raw_data is None:
        return pd.DataFrame()
    if raw_data.empty:
        return pd.DataFrame()
    return pd.DataFrame(raw_data.dropna())


@log_start_end(log=logger)
def stoch(
    data: pd.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
):
    """Stochastic oscillator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    Returns
    -------
    pd.DataFrame
        Dataframe of technical indicator
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.stoch(
            high=data["High"],
            low=data["Low"],
            close=data[close_col],
            k=fastkperiod,
            d=slowdperiod,
            smooth_k=slowkperiod,
        ).dropna()
    )


@log_start_end(log=logger)
def fisher(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Fisher Transform

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    window: int
        Length for indicator window
    Returns
    -------
    df_ta: pd.DataFrame
        Dataframe of technical indicator
    """
    # Daily
    close_col = ta_helpers.check_columns(data, close=False)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.fisher(high=data["High"], low=data["Low"], length=window).dropna()
    )


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
    -------
    pd.DataFrame
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

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.clenow(df["Close"])
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
    annualized_coef = (np.exp(coef) ** 252) - 1

    return r2, annualized_coef, pd.Series(lr.predict(X))


@log_start_end(log=logger)
def demark_seq(values: pd.Series) -> pd.DataFrame:
    """Get the integer value for demark sequential indicator

    Parameters
    ----------
    values: pd.Series
        Series of close values

    Returns
    -------
    pd.DataFrame
        Dataframe of UP and DOWN sequential indicators

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.demark(df["Close"])
    """
    return ta.td_seq(values, asint=True)
