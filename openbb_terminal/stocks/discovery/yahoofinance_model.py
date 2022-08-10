""" Yahoo Finance Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


def get_df(url: str) -> pd.DataFrame:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36"
            "  (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        )
    }
    html = requests.get(url, headers=headers).text
    dfs = pd.read_html(html)[0]
    return dfs


@log_start_end(log=logger)
def get_gainers() -> pd.DataFrame:
    """Get top gainers. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Stock Gainers
    """
    return get_df("https://finance.yahoo.com/screener/predefined/day_gainers")


@log_start_end(log=logger)
def get_losers() -> pd.DataFrame:
    """Get top losers. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Stock Losers
    """
    return get_df("https://finance.yahoo.com/screener/predefined/day_losers")


@log_start_end(log=logger)
def get_ugs() -> pd.DataFrame:
    """Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.
    [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Undervalued stocks
    """
    return get_df(
        "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks"
    )


@log_start_end(log=logger)
def get_gtech() -> pd.DataFrame:
    """Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Growth technology stocks
    """
    return get_df(
        "https://finance.yahoo.com/screener/predefined/growth_technology_stocks"
    )


@log_start_end(log=logger)
def get_active() -> pd.DataFrame:
    """Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most active stocks
    """
    return get_df("https://finance.yahoo.com/screener/predefined/most_actives")


@log_start_end(log=logger)
def get_ulc() -> pd.DataFrame:
    """Get Yahoo Finance potentially undervalued large cap stocks.
    [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most undervalued large cap stocks
    """
    return get_df(
        "https://finance.yahoo.com/screener/predefined/undervalued_large_caps"
    )


@log_start_end(log=logger)
def get_asc() -> pd.DataFrame:
    """Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.
    [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most aggressive small cap stocks
    """
    return get_df("https://finance.yahoo.com/screener/predefined/aggressive_small_caps")
