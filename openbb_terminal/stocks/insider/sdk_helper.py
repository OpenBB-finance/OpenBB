"""Insider SDK Helpers"""
__docformat__ = "numpy"

import pandas as pd

from openbb_terminal.stocks.insider import openinsider_model


def stats(symbol: str) -> pd.DataFrame:
    """Get OpenInsider stats for ticker

    Parameters
    ----------
    symbol : str
        Ticker to get insider stats for

    Returns
    -------
    pd.DataFrame
        DataFrame of insider stats

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.stats("AAPL")
    """
    link = f"http://openinsider.com/screener?s={symbol}"
    return openinsider_model.get_open_insider_data(link, has_company_name=False)


def insider_filter(preset: str) -> pd.DataFrame:
    """GEt insider trades based on preset filter

    Parameters
    ----------
    preset : str
       Name of preset filter

    Returns
    -------
    pd.DataFrame
        DataFrame of filtered insider data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb

    In order to filter, we pass one of the predefined .ini filters from OpenBBUserData/presets/stocks/insider
    >>> filter = "Gold-Silver"
    >>> insider_trades = openbb.stocks.ins.filter(filter)
    """
    url = openinsider_model.get_open_insider_link(preset)
    return openinsider_model.get_open_insider_data(url, has_company_name=True)
