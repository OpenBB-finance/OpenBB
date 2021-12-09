""" Fred Model """
__docformat__ = "numpy"

from typing import List, Tuple

import fred
import pandas as pd
from fredapi import Fred

from gamestonk_terminal import config_terminal as cfg


def get_series_notes(series_term: str) -> pd.DataFrame:
    """Get Series notes. [Source: FRED]

    Parameters
    ----------
    series_term : str
        Search for this series term

    Returns
    ----------
    pd.DataFrame
        DataFrame of matched series
    """

    fred.key(cfg.API_FRED_KEY)
    d_series = fred.search(series_term)

    if "seriess" not in d_series:
        return pd.DataFrame()
    if not d_series["seriess"]:
        return pd.DataFrame()
    df_fred = pd.DataFrame(d_series["seriess"])
    df_fred["notes"] = df_fred["notes"].fillna("No description provided.")
    return df_fred


def get_series_ids(series_term: str, num: int) -> Tuple[List[str], List[str]]:
    """Get Series IDs. [Source: FRED]

    Parameters
    ----------
    series_term : str
        Search for this series term
    num : int
        Maximum number of series IDs to output

    Returns
    ----------
    List[str]
        List of series IDs
    List[str]
        List of series Titles
    """
    fred.key(cfg.API_FRED_KEY)
    d_series = fred.search(series_term)

    if "seriess" not in d_series:
        return [], []

    if not d_series["seriess"]:
        return [], []

    df_series = pd.DataFrame(d_series["seriess"])
    df_series = df_series.sort_values(by=["popularity"], ascending=False).head(num)
    return df_series["id"].values, df_series["title"].values


def get_series_data(series_id: str, start: str):
    """Get Series data. [Source: FRED]

    Parameters
    ----------
    series_id : str
        Series ID to get data from
    start : str
        Start date to get data from, format yyyy-mm-dd

    Returns
    ----------
    pd.DataFrame
        Series data
    """
    fredapi_client = Fred(cfg.API_FRED_KEY)
    return fredapi_client.get_series(series_id, start)
