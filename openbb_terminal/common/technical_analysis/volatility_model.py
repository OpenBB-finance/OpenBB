"""Volatility Technical Indicators"""
__docformat__ = "numpy"

import logging
import numpy as np
import pandas as pd
import pandas_ta as ta

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end

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

@log_start_end(log=logger)
def rvol(
    data:pd.DataFrame,
    lower_q:float = 0.25,
    upper_q: float = 0.75
) -> pd.DataFrame:
    """Returns a DataFrame of realized volatility quantiles.
    
    Paramters
    ---------
    data: pd.DataFrame
        DataFrame of the OHLC data.
    lower_q: float (default = 0.25)
        The lower quantile to calculate the realized volatility over time for.
    upper_q: float (default = 0.75)
        The upper quantile to calculate the realized volatility over time for.
    
    Returns
    -------
    pd.DataFrame: rvol_cones
        DataFrame of realized volatility quantiles.
    
    Examples
    --------
    df = get_rvol_cones(symbol = "AAPL")
    
    df = get_rvol_cones(symbol = "AAPL", lower_q = 0.10, upper_q = 0.90)
    """
    lower_q_label = str((int(lower_q*100)))
    upper_q_label = str((int(upper_q*100)))
    
    rvol_cones: DataFrame = pd.DataFrame()
    quantiles = [lower_q, upper_q]
    windows = [3,10,30,60,90,120,150,180,210,240]
    data = data
    min_ = []
    max_ = []
    median = []
    top_q = []
    bottom_q = []
    realized = []
    data.index = data.index.date
    data = pd.DataFrame(data).sort_index(ascending = False)

    def realized_vol(data, window=30):
        """Helper function for calculating realized volatility."""

        log_return = (data["Close"] / data["Close"].shift(1)).apply(np.log)

        return log_return.rolling(window=window, center=False).std() * np.sqrt(252)
    
    for window in windows:
        
            # Looping to build a dataframe with realized volatility over each window.
        
        estimator = realized_vol(window=window,data=data)
        min_.append(estimator.min())
        max_.append(estimator.max())
        median.append(estimator.median())
        top_q.append(estimator.quantile(quantiles[1]))
        bottom_q.append(estimator.quantile(quantiles[0]))
        realized.append(estimator[-1])
    
    df = [realized, min_, bottom_q, median, top_q, max_]
    pd.DataFrame(df).columns = windows
    df_windows = list(windows)
    df = pd.DataFrame(df, columns=df_windows)
    df = df.rename(index = {0:'Realized', 1: 'Min', 2:'Lower 'f"{lower_q_label}"'%', 3:'Median', 4:'Upper 'f"{upper_q_label}"'%', 5: 'Max'})
    rvol_cones = df.copy()

    return rvol_cones.transpose()
