""" Yahoo Finance Model """
__docformat__ = "numpy"

import pandas as pd
import requests


def get_gainers() -> pd.DataFrame:
    """Get top gainers. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Stock Gainers
    """
    url_gainers = "https://finance.yahoo.com/screener/predefined/day_gainers"

    return pd.read_html(requests.get(url_gainers).text)[0]


def get_losers() -> pd.DataFrame:
    """Get top losers. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Stock Losers
    """
    url_losers = "https://finance.yahoo.com/screener/predefined/day_losers"

    return pd.read_html(requests.get(url_losers).text)[0]


def get_ugs() -> pd.DataFrame:
    """Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Undervalued stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks"

    data = pd.read_html(requests.get(url).text)[0]
    data = data.iloc[:, :-1]
    return data


def get_gtech() -> pd.DataFrame:
    """Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Growth technology stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/growth_technology_stocks"

    data = pd.read_html(requests.get(url).text)[0]
    data = data.iloc[:, :-1]
    return data


def get_active() -> pd.DataFrame:
    """Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most active stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/most_actives"

    data = pd.read_html(requests.get(url).text)[0]
    return data


def get_ulc() -> pd.DataFrame:
    """Get Yahoo Finance potentially undervalued large cap stocks. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most undervalued large cap stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/undervalued_large_caps"

    data = pd.read_html(requests.get(url).text)[0]
    return data


def get_asc() -> pd.DataFrame:
    """Get Yahoo Finance small cap stocks with earnings growth rates better than 25%. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most aggressive small cap stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/aggressive_small_caps"

    data = pd.read_html(requests.get(url).text)[0]
    return data
