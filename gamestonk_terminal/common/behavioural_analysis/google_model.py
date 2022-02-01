"""Google Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
from pytrends.request import TrendReq

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_mentions(ticker: str) -> pd.DataFrame:
    """Get interest over time from google api [Source: google]

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe of interest over time
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[ticker])
    return pytrend.interest_over_time()


@log_start_end(log=logger)
def get_regions(ticker: str) -> pd.DataFrame:
    """Get interest by region from google api [Source: google]

    Parameters
    ----------
    ticker : str
        Ticker to look at

    Returns
    -------
    pd.DataFrame
        Dataframe of interest by region
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[ticker])
    return pytrend.interest_by_region()


@log_start_end(log=logger)
def get_queries(ticker: str) -> pd.DataFrame:
    """Get related queries from google api [Source: google]

    Parameters
    ----------
    ticker : str
        Stock ticker to compare

    Returns
    -------
    pd.DataFrame
        Dataframe of related queries
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[ticker])
    return pytrend.related_queries()


@log_start_end(log=logger)
def get_rise(ticker: str) -> pd.DataFrame:
    """Get top rising related queries with this stock's query [Source: google]

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe containing rising related queries
    """
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=[ticker])
    df_related_queries = pytrend.related_queries()
    return df_related_queries[ticker]["rising"]
