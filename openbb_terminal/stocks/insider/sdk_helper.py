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


def lcb() -> pd.DataFrame:
    """Get latest cluster buys

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.lcb()
    """
    return openinsider_model.get_print_insider_data("lcb")


def lpsb() -> pd.DataFrame:
    """Get latest penny stock buys

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.lpsb()
    """
    return openinsider_model.get_print_insider_data("lpsb")


def lit() -> pd.DataFrame:
    """Get latest insider trades

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.lit()
    """
    return openinsider_model.get_print_insider_data("lit")


def lip() -> pd.DataFrame:
    """Get latest insider purchases

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.lip()
    """
    return openinsider_model.get_print_insider_data("lip")


def blip() -> pd.DataFrame:
    """Get latest insider purchases > 25k

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.blip()
    """
    return openinsider_model.get_print_insider_data("blip")


def blop() -> pd.DataFrame:
    """Get latest officer purchases > 25k

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.blop()
    """
    return openinsider_model.get_print_insider_data("blop")


def blcp() -> pd.DataFrame:
    """Get latest CEO/CFO purchases > 25k

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.blcp()
    """
    return openinsider_model.get_print_insider_data("blcp")


def lis() -> pd.DataFrame:
    """Get latest insider sales

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.lis()
    """
    return openinsider_model.get_print_insider_data("lis")


def blis() -> pd.DataFrame:
    """Get latest insider sales > 100k

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.blis()
    """
    return openinsider_model.get_print_insider_data("blis")


def blos() -> pd.DataFrame:
    """Get latest officer sales > 100k

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.blos()
    """
    return openinsider_model.get_print_insider_data("blos")


def blcs() -> pd.DataFrame:
    """Get latest CEO/CFO sales > 100k

    Returns
    -------
    pd.DataFrame
        DataFrame of latest insider trades

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.stocks.ins.blcs()
    """
    return openinsider_model.get_print_insider_data("blcs")
