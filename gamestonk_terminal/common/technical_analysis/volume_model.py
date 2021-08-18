"""Volume Technical Analysis"""
__docformat__ = "numpy"

import pandas as pd
import pandas_ta as ta


def ad(df_stock: pd.DataFrame, use_open: bool) -> pd.DataFrame:
    """Calculate AD technical indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    use_open : bool
        Whether to use open prices

    Returns
    -------
    pd.DataFrame
        Dataframe with techinical indicator
    """
    if use_open:
        df_ta = ta.ad(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            volume=df_stock["Volume"],
            open_=df_stock["Open"],
        ).dropna()
    # Do not use open stock values
    else:
        df_ta = ta.ad(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            volume=df_stock["Volume"],
        ).dropna()
    return pd.DataFrame(df_ta)


def obv(s_interval: str, df_stock: pd.DataFrame) -> pd.DataFrame:
    """On Balance Volume

    Parameters
    ----------
    s_interval: str
        Stock data interval
    df_stock: pd.DataFrame
        Dataframe of stock prices

    Returns
    -------
    pd.DataFrame
        Dataframe with techinical indicator
    """
    # Daily
    if s_interval == "1440min":
        df_ta = ta.obv(close=df_stock["Adj Close"], volume=df_stock["Volume"]).dropna()

    # Intraday
    else:
        df_ta = ta.obv(close=df_stock["Close"], volume=df_stock["Volume"]).dropna()

    return df_ta
