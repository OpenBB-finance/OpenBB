""" Yahoo Finance Model """
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.discovery.disc_helpers import get_df

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_gainers() -> pd.DataFrame:
    """Get top gainers. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Stock Gainers
    """

    df_gainers = get_df("https://finance.yahoo.com/screener/predefined/day_gainers")[0]
    df_gainers.dropna(how="all", axis=1, inplace=True)
    df_gainers = df_gainers.replace(float("NaN"), "")
    if df_gainers.empty:
        console.print("No gainers found.")

    return df_gainers


@log_start_end(log=logger)
def get_losers() -> pd.DataFrame:
    """Get top losers. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Stock Losers
    """

    df_losers = get_df("https://finance.yahoo.com/screener/predefined/day_losers")[0]
    df_losers.dropna(how="all", axis=1, inplace=True)
    df_losers = df_losers.replace(float("NaN"), "")

    if df_losers.empty:
        console.print("No losers found.")
    return df_losers


@log_start_end(log=logger)
def get_ugs() -> pd.DataFrame:
    """Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.
    [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Undervalued stocks
    """

    df = get_df(
        "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks"
    )[0]
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    return df


@log_start_end(log=logger)
def get_gtech() -> pd.DataFrame:
    """Get technology stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Growth technology stocks
    """

    df = get_df(
        "https://finance.yahoo.com/screener/predefined/growth_technology_stocks"
    )[0]
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    return df


@log_start_end(log=logger)
def get_active() -> pd.DataFrame:
    """Get stocks ordered in descending order by intraday trade volume. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most active stocks
    """

    df = get_df("https://finance.yahoo.com/screener/predefined/most_actives")[0]
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    return df


@log_start_end(log=logger)
def get_ulc() -> pd.DataFrame:
    """Get Yahoo Finance potentially undervalued large cap stocks.
    [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most undervalued large cap stocks
    """

    df = get_df("https://finance.yahoo.com/screener/predefined/undervalued_large_caps")[
        0
    ]
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    return df


@log_start_end(log=logger)
def get_asc() -> pd.DataFrame:
    """Get Yahoo Finance small cap stocks with earnings growth rates better than 25%.
    [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most aggressive small cap stocks
    """

    df = get_df("https://finance.yahoo.com/screener/predefined/aggressive_small_caps")[
        0
    ]
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    return df


@log_start_end(log=logger)
def get_hotpenny() -> pd.DataFrame:
    """Get Yahoo Finance hot penny stocks. [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Hottest penny stocks
    """
    return get_df(
        "https://finance.yahoo.com/u/yahoo-finance/watchlists/most-active-penny-stocks/"
    )[1]
