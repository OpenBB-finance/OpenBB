""" Fred Model """
__docformat__ = "numpy"

import logging
from typing import Dict, List, Tuple
from requests import HTTPError

import fred
import pandas as pd
import requests
from fredapi import Fred

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent
from gamestonk_terminal.rich_config import console

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
    if r.status_code == 200:
        payload = r.json()

    elif r.status_code >= 500:
        payload = {}
    # cover invalid api keys & series does not exist
    elif r.status_code == 400:
        payload = {}
        if "api_key" in r.json()["error_message"]:
            console.print("[red]Invalid API Key[/red]\n")
            logger.error("[red]Invalid API Key[/red]\n")
        elif "The series does not exist" in r.json()["error_message"]:
            console.print(f"[red]{series_id} not found[/red].\n")
            logger.error("%s not found", str(series_id))
        else:
            console.print(r.json()["error_message"])
            logger.error(r.json()["error_message"])

    return payload


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

    df_fred = pd.DataFrame()

    if "error_message" in d_series:
        if "api_key" in d_series["error_message"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(d_series["error_message"])
    else:

        if "seriess" in d_series:
            if d_series["seriess"]:
                df_fred = pd.DataFrame(d_series["seriess"])
                df_fred["notes"] = df_fred["notes"].fillna("No description provided.")
            else:
                console.print("No matches found. \n")
        else:
            console.print("No matches found. \n")

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

    # Cover invalid api and empty search terms
    if "error_message" in d_series:
        if "api_key" in d_series["error_message"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(d_series["error_message"])
        return [], []

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
    df = pd.DataFrame()

    try:
        fredapi_client = Fred(cfg.API_FRED_KEY)
        df = fredapi_client.get_series(series_id, start)
    # Series does not exist & invalid api keys
    except HTTPError as e:
        console.print(e)

    return df
