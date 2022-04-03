"""Rolling Statistics"""
__docformat__ = "numpy"

import logging
from typing import Tuple

import pandas as pd
import pandas_ta as ta

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_rolling_avg(df: pd.DataFrame, length: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return rolling mean and standard deviation

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of target data
    length : int
        Length of rolling window

    Returns
    -------
    pd.DataFrame :
        Dataframe of rolling mean
    pd.DataFrame :
        Dataframe of rolling standard deviation
    """
    rolling_mean = df.rolling(length, center=True, min_periods=1).mean()
    rolling_std = df.rolling(length, center=True, min_periods=1).std()

    return pd.DataFrame(rolling_mean), pd.DataFrame(rolling_std)


@log_start_end(log=logger)
def get_spread(df: pd.DataFrame, length: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Standard Deviation and Variance

    Parameters
    ----------
    df_stock : pd.DataFrame
        DataFrame of targeted data

    Returns
    -------
    df_sd : pd.DataFrame
        Dataframe of rolling standard deviation
    df_var : pd.DataFrame
        Dataframe of rolling standard deviation
    """
    df_sd = ta.stdev(
        close=df,
        length=length,
    ).dropna()
    df_var = ta.variance(
        close=df,
        length=length,
    ).dropna()

    return pd.DataFrame(df_sd), pd.DataFrame(df_var)


@log_start_end(log=logger)
def get_quantile(
    df: pd.DataFrame, length: int, quantile_pct: float
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Overlay Median & Quantile

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of targeted data
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
    df_med = ta.median(close=df, length=length).dropna()
    df_quantile = ta.quantile(
        df,
        length=length,
        q=quantile_pct,
    ).dropna()

    return pd.DataFrame(df_med), pd.DataFrame(df_quantile)


@log_start_end(log=logger)
def get_skew(df: pd.DataFrame, length: int) -> pd.DataFrame:
    """Skewness Indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of targeted data
    length : int
        Length of window

    Returns
    -------
    df_skew : pd.DataFrame
        Dataframe of rolling skew
    """
    df_skew = ta.skew(close=df, length=length).dropna()
    return df_skew


@log_start_end(log=logger)
def get_kurtosis(df: pd.DataFrame, length: int) -> pd.DataFrame:
    """Kurtosis Indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of targeted data
    length : int
        Length of window

    Returns
    -------
    df_kurt : pd.DataFrame
        Dataframe of rolling kurtosis
    """
    df_kurt = ta.kurtosis(close=df, length=length).dropna()
    return df_kurt
