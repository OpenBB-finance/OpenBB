"""Google Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pytrends
from pytrends.request import TrendReq

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_mentions(symbol: str) -> pd.DataFrame:
    """Get interest over time from google api [Source: google]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of interest over time
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[symbol])
    return pytrend.interest_over_time()


@log_start_end(log=logger)
def get_regions(symbol: str) -> pd.DataFrame:
    """Get interest by region from google api [Source: google]

    Parameters
    ----------
    symbol: str
        Ticker symbol to look at

    Returns
    -------
    pd.DataFrame
        Dataframe of interest by region
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[symbol])
    try:
        return pytrend.interest_by_region().sort_values([symbol], ascending=False)
    except pytrends.exceptions.ResponseError:
        return pd.DataFrame()


@log_start_end(log=logger)
def get_queries(symbol: str, limit: int = 10) -> pd.DataFrame:
    """Get related queries from google api [Source: google]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol to compare
    limit: int
        Number of queries to show

    Returns
    -------
    dict : {'top': pd.DataFrame or None, 'rising': pd.DataFrame or None}

    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[symbol])
    df_related_queries = pytrend.related_queries()
    df_related_queries = df_related_queries[symbol]["top"].head(limit)
    df_related_queries["value"] = df_related_queries["value"].apply(
        lambda x: str(x) + "%"
    )
    return df_related_queries


@log_start_end(log=logger)
def get_rise(symbol: str, limit: int = 10) -> pd.DataFrame:
    """Get top rising related queries with this stock's query [Source: google]

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
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[symbol])
    df_related_queries = pytrend.related_queries()
    return df_related_queries[symbol]["rising"].head(limit)
