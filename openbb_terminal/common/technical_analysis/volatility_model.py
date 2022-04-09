"""Volatility Technical Indicators"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

MAMODES = ["ema", "sma", "wma", "hma", "zlma"]


@log_start_end(log=logger)
def bbands(
    close_values: pd.Series, length: int = 15, n_std: float = 2, mamode: str = "ema"
) -> pd.DataFrame:
    """Calculate Bollinger Bands

    Parameters
    ----------
    close_values : pd.DataFrame
        DataFrame of sclose prices
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
    return pd.DataFrame(
        ta.bbands(
            close=close_values,
            length=length,
            std=n_std,
            mamode=mamode,
        )
    ).dropna()


@log_start_end(log=logger)
def donchian(
    high_prices: pd.Series,
    low_prices: pd.Series,
    upper_length: int = 20,
    lower_length: int = 20,
) -> pd.DataFrame:
    """Calculate Donchian Channels

    Parameters
    ----------
    high_prices : pd.DataFrame
        High prices
    low_prices : pd.DataFrame
        Low prices
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel

    Returns
    -------
    pd.DataFrame
        Dataframe of upper and lower channels
    """
    return pd.DataFrame(
        ta.donchian(
            high=high_prices,
            low=low_prices,
            upper_length=upper_length,
            lower_length=lower_length,
        ).dropna()
    )


@log_start_end(log=logger)
def kc(
    high_prices: pd.Series,
    low_prices: pd.Series,
    close_prices: pd.Series,
    length: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
) -> pd.DataFrame:
    """Keltner Channels

    Parameters
    ----------
    high_values : pd.DataFrame
        High prices
    low_values : pd.DataFrame
        Low prices
    close_values : pd.DataFrame
        Close prices
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
    return pd.DataFrame(
        ta.kc(
            high=high_prices,
            low=low_prices,
            close=close_prices,
            length=length,
            scalar=scalar,
            mamode=mamode,
            offset=offset,
        ).dropna()
    )
