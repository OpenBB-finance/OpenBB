"""Volatility Technical Indicators"""
__docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta


def bbands(
    s_interval: str, df_stock: pd.DataFrame, length: int, n_std: float, mamode: str
):
    """Calculate Bollinger Bands

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        DataFrame of stock data
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
    # Daily
    if s_interval == "1440min":
        df_ta = ta.bbands(
            close=df_stock["Adj Close"],
            length=length,
            std=n_std,
            mamode=mamode,
        ).dropna()

    # Intraday
    else:
        df_ta = ta.bbands(
            close=df_stock["Close"],
            length=length,
            std=n_std,
            mamode=mamode,
        ).dropna()

    return df_ta
