"""Volume Technical Analysis"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pandas_ta as ta

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def ad(data: pd.DataFrame, use_open: bool = False) -> pd.DataFrame:
    """Calculate AD technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of prices with OHLC and Volume
    use_open : bool
        Whether to use open prices

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator
    """
    kwargs = {}
    if use_open:
        kwargs["Open"] = data["Open"]
    df_ta = ta.ad(
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        volume=data["Volume"],
        **kwargs
    ).dropna()
    return pd.DataFrame(df_ta)


@log_start_end(log=logger)
def adosc(
    data: pd.DataFrame, use_open: bool = False, fast: int = 3, slow: int = 10
) -> pd.DataFrame:
    """Calculate AD oscillator technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    use_open : bool
        Whether to use open prices
    fast: int
        Fast value
    slow: int
        Slow value

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator
    """
    if use_open:
        df_ta = ta.adosc(
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            volume=data["Volume"],
            open_=data["Open"],
            fast=fast,
            slow=slow,
        ).dropna()
    else:
        df_ta = ta.adosc(
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            volume=data["Volume"],
            fast=fast,
            slow=slow,
        ).dropna()
    return pd.DataFrame(df_ta)


@log_start_end(log=logger)
def obv(data: pd.DataFrame) -> pd.DataFrame:
    """On Balance Volume

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of OHLC prices

    Returns
    -------
    pd.DataFrame
        Dataframe with technical indicator
    """
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return pd.DataFrame()
    if "Volume" not in data.columns:
        console.print("[red]Volume column not found[/red]\n")
        return pd.DataFrame()
    return pd.DataFrame(ta.obv(close=data[close_col], volume=data["Volume"]).dropna())
