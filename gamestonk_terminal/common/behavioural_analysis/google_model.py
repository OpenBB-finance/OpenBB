"""Google Model"""
__docformat__ = "numpy"

import pandas as pd
from pytrends.request import TrendReq


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
