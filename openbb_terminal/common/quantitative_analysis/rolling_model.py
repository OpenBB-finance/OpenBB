"""Rolling Statistics"""
__docformat__ = "numpy"

import logging
from typing import Tuple

import pandas as pd
import pandas_ta as ta

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_rolling_avg(
    data: pd.DataFrame, window: int = 14
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return rolling mean and standard deviation

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of target data
    window: int
        Length of rolling window

    Returns
    -------
    pd.DataFrame:
        Dataframe of rolling mean
    pd.DataFrame:
        Dataframe of rolling standard deviation
    """
    rolling_mean = data.rolling(window, center=True, min_periods=1).mean()
    rolling_std = data.rolling(window, center=True, min_periods=1).std()

    return pd.DataFrame(rolling_mean), pd.DataFrame(rolling_std)


@log_start_end(log=logger)
def get_spread(
    data: pd.DataFrame, window: int = 14
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Standard Deviation and Variance

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame of targeted data
    window: int
        Length of window

    Returns
    -------
    df_sd: pd.DataFrame
        Dataframe of rolling standard deviation
    df_var: pd.DataFrame
        Dataframe of rolling standard deviation
    """
    df_sd = ta.stdev(
        close=data,
        length=window,
    ).dropna()
    df_var = ta.variance(
        close=data,
        length=window,
    ).dropna()

    return pd.DataFrame(df_sd), pd.DataFrame(df_var)


@log_start_end(log=logger)
def get_quantile(
    data: pd.DataFrame, limit: int = 14, quantile_pct: float = 0.5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Overlay Median & Quantile

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of targeted data
    limit : int
        Length of window
    quantile_pct: float
        Quantile to display

    Returns
    -------
    df_med : pd.DataFrame
        Dataframe of median prices over window
    df_quantile : pd.DataFrame
        Dataframe of gievn quantile prices over window
    """
    df_med = ta.median(close=data, length=limit).dropna()
    df_quantile = ta.quantile(
        data,
        length=limit,
        q=quantile_pct,
    ).dropna()

    return pd.DataFrame(df_med), pd.DataFrame(df_quantile)


@log_start_end(log=logger)
def get_skew(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Skewness Indicator

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of targeted data
    window : int
        Length of window

    Returns
    -------
    data_skew : pd.DataFrame
        Dataframe of rolling skew
    """
    df_skew = ta.skew(close=data, length=window).dropna()
    return df_skew


@log_start_end(log=logger)
def get_kurtosis(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Kurtosis Indicator

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of targeted data
    window: int
        Length of window

    Returns
    -------
    df_kurt : pd.DataFrame
        Dataframe of rolling kurtosis
    """
    df_kurt = ta.kurtosis(close=data, length=window).dropna()
    return df_kurt
