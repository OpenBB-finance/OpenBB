"""Volume Technical Analysis"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def ad(df_stock: pd.DataFrame, use_open: bool = False) -> pd.DataFrame:
    """Calculate AD technical indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices with OHLC and Volume
    use_open : bool
        Whether to use open prices

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator
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


@log_start_end(log=logger)
def adosc(
    df_stock: pd.DataFrame, use_open: bool = False, fast: int = 3, slow: int = 10
) -> pd.DataFrame:
    """Calculate AD oscillator technical indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    use_open : bool
        Whether to use open prices

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator
    """
    if use_open:
        df_ta = ta.adosc(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            volume=df_stock["Volume"],
            open_=df_stock["Open"],
            fast=fast,
            slow=slow,
        ).dropna()
    else:
        df_ta = ta.adosc(
            high=df_stock["High"],
            low=df_stock["Low"],
            close=df_stock["Close"],
            volume=df_stock["Volume"],
            fast=fast,
            slow=slow,
        ).dropna()
    return pd.DataFrame(df_ta)


@log_start_end(log=logger)
def obv(df_stock: pd.DataFrame) -> pd.DataFrame:
    """On Balance Volume

    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of stock prices

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator
    """
    return pd.DataFrame(
        ta.obv(close=df_stock["Adj Close"], volume=df_stock["Volume"]).dropna()
    )
