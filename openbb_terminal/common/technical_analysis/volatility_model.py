"""Volatility Technical Indicators"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from openbb_terminal.decorators import log_start_end
from openbb_terminal.common.technical_analysis import ta_helpers

logger = logging.getLogger(__name__)

MAMODES = ["ema", "sma", "wma", "hma", "zlma"]


@log_start_end(log=logger)
def bbands(
    data: pd.DataFrame, window: int = 15, n_std: float = 2, mamode: str = "ema"
) -> pd.DataFrame:
    """Calculate Bollinger Bands

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    window : int
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
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.bbands(
            close=data[close_col],
            length=window,
            std=n_std,
            mamode=mamode,
        )
    ).dropna()


@log_start_end(log=logger)
def donchian(
    data: pd.DataFrame,
    upper_length: int = 20,
    lower_length: int = 20,
) -> pd.DataFrame:
    """Calculate Donchian Channels

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel

    Returns
    -------
    pd.DataFrame
        Dataframe of upper and lower channels
    """
    close_col = ta_helpers.check_columns(data, close=False)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.donchian(
            high=data["High"],
            low=data["Low"],
            upper_length=upper_length,
            lower_length=lower_length,
        ).dropna()
    )


@log_start_end(log=logger)
def kc(
    data: pd.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
) -> pd.DataFrame:
    """Keltner Channels

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset : int
        Offset value

    Returns
    -------
    pd.DataFrame
        Dataframe of rolling kc
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.kc(
            high=data["High"],
            low=data["Low"],
            close=data[close_col],
            length=window,
            scalar=scalar,
            mamode=mamode,
            offset=offset,
        ).dropna()
    )


@log_start_end(log=logger)
def atr(
    data: pd.DataFrame,
    window: int = 14,
    mamode: str = "ema",
    offset: int = 0,
) -> pd.DataFrame:
    """Average True Range

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    window : int
        Length of window
    mamode: str
        Type of filter
    offset : int
        Offset value

    Returns
    -------
    pd.DataFrame
        Dataframe of atr
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.atr(
            high=data["High"],
            low=data["Low"],
            close=data[close_col],
            length=window,
            mamode=mamode,
            offset=offset,
        ).dropna()
    )
