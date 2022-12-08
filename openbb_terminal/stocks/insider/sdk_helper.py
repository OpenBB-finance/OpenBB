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
