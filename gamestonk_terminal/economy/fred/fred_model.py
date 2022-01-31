""" Fred Model """
__docformat__ = "numpy"

import logging
from typing import Dict, List, Tuple

import fred
import pandas as pd
import requests
from fredapi import Fred

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def check_series_id(series_id: str) -> Tuple[bool, Dict]:
    """Checks if series ID exists in fred

    Parameters
    ----------
    series_id: str
        Series ID to check

    Returns
    -------
    bool:
        Boolean if series ID exists
    dict:
        Dictionary of series information
    """
    url = f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={cfg.API_FRED_KEY}&file_type=json"
    r = requests.get(url, headers={"User-Agent": get_user_agent()})
    # The above returns 200 if series is found
    # There seems to be an occasional bug giving a 503 response where the json decoding fails
    if r.status_code >= 500:
        return False, {}
    return r.status_code == 200, r.json()


@log_start_end(log=logger)
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


@log_start_end(log=logger)
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


@log_start_end(log=logger)
def get_series_data(series_id: str, start: str) -> pd.DataFrame:
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
