"""Google Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
from pytrends.request import TrendReq

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_mentions(symbol: str) -> pd.DataFrame:
    """Get interest over time from google api [Source: google].

    Parameters
    ----------
    symbol: str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of interest over time
    """
    try:
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[symbol])
        return pytrend.interest_over_time()

    except Exception as e:
        if pytrend.google_rl:
            console.print(f"[red]Too many requests: {pytrend.google_rl}[/red]\n")
        else:
            console.print(f"[red]{str(e)}[/red]\n")

        return pd.DataFrame()


@log_start_end(log=logger)
def get_regions(symbol: str) -> pd.DataFrame:
    """Get interest by region from google api [Source: google].

    Parameters
    ----------
    symbol: str
        Ticker symbol to look at

    Returns
    -------
    pd.DataFrame
        Dataframe of interest by region
    """

    try:
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[symbol])
        return pytrend.interest_by_region().sort_values([symbol], ascending=False)

    except Exception as e:
        if pytrend.google_rl:
            console.print(f"[red]Too many requests: {pytrend.google_rl}[/red]\n")
        else:
            console.print(f"[red]{str(e)}[/red]\n")

        return pd.DataFrame()


@log_start_end(log=logger)
def get_queries(symbol: str, limit: int = 10) -> pd.DataFrame:
    """Get related queries from google api [Source: google].

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to compare
    limit: int
        Number of queries to show

    Returns
    -------
    pd.DataFrame
        Dataframe of related queries
    """
    try:
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[symbol])
        df = pytrend.related_queries()
        df = df[symbol]["top"].head(limit)
        df["value"] = df["value"].apply(lambda x: f"{str(x)}%")
        return df

    except Exception as e:
        if pytrend.google_rl:
            console.print(f"[red]Too many requests: {pytrend.google_rl}[/red]\n")
        else:
            console.print(f"[red]{str(e)}[/red]\n")

        return pd.DataFrame()


@log_start_end(log=logger)
def get_rise(symbol: str, limit: int = 10) -> pd.DataFrame:
    """Get top rising related queries with this stock's query [Source: google].

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of queries to show

    Returns
    -------
    pd.DataFrame
        Dataframe containing rising related queries
    """
    try:
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[symbol])
        df = pytrend.related_queries()
        df = df[symbol]["rising"].head(limit)
        return df

    except Exception as e:
        if pytrend.google_rl:
            console.print(f"[red]Too many requests: {pytrend.google_rl}[/red]\n")
        else:
            console.print(f"[red]{str(e)}[/red]\n")

        return pd.DataFrame()
