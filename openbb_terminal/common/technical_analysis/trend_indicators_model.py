"""Trend Indicators Technical Analysis Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def adx(
    data: pd.DataFrame,
    window: int = 14,
    scalar: int = 100,
    drift: int = 1,
) -> pd.DataFrame:
    """ADX technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with OHLC price data
    window: int
        Length of window
    scalar: int
        Scalar variable
    drift: int
        Drift variable

    Returns
    -------
    pd.DataFrame
        DataFrame with adx indicator
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.adx(
            high=data["High"],
            low=data["Low"],
            close=data[close_col],
            length=window,
            scalar=scalar,
            drift=drift,
        ).dropna()
    )


@log_start_end(log=logger)
def aroon(data: pd.DataFrame, window: int = 25, scalar: int = 100) -> pd.DataFrame:
    """Aroon technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with OHLC price data
    window : int
        Length of window
    scalar : int
        Scalar variable

    Returns
    -------
    pd.DataFrame
        DataFrame with aroon indicator
    """
    close_col = ta_helpers.check_columns(data, close=False)
    if close_col is None:
        return pd.DataFrame()
    return pd.DataFrame(
        ta.aroon(
            high=data["High"],
            low=data["Low"],
            length=window,
            scalar=scalar,
        ).dropna()
    )
