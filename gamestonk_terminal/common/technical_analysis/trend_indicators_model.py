"""Trend Indicators Technical Analysis Model"""
__docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta


def adx(s_interval: str, df_stock: pd.DataFrame, length: int, scalar: int, drift: int):
    """ADX technical indicator

    Parameters
    ----------
    s_interval : str
        Interval of stock data
    df_stock : pd.DataFrame
        Dataframe with prices
    length: int
        Length of window
    scalar: int
        Scalar variable
    drift: int
        Drift variable

    Returns
    -------
    df_ta: pd.DataFrame
        DataFrame with adx indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.adx(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Adj Close"],
            length=length,
            scalar=scalar,
            drift=drift,
        ).dropna()

    # Intraday
    else:
        df_ta = ta.adx(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            length=length,
            scalar=scalar,
            drift=drift,
        ).dropna()

    return df_ta


def aroon(df_stock: pd.DataFrame, length: int, scalar: int) -> pd.DataFrame:
    """Aroon technical indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window
    scalar : int
        Scalar variable

    Returns
    -------
    df_ta: pd.DataFrame
        DataFrame with aroon indicator
    """

    df_ta = ta.aroon(
        high=df_stock["High"],
        low=df_stock["Low"],
        length=length,
        scalar=scalar,
    ).dropna()

    return pd.DataFrame(df_ta)
