""" Fred Model """
__docformat__ = "numpy"

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from requests import HTTPError

import fred
import pandas as pd
import requests
from fredapi import Fred

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.rich_config import console

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
            console.print(f"[red]{series_id} not found.[/red]\n")
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
def get_series_data(series_id: str, start: str = None, end: str = None) -> pd.DataFrame:
    """Get Series data. [Source: FRED]
    Parameters
    ----------
    series_id : str
        Series ID to get data from
    start : str
        Start date to get data from, format yyyy-mm-dd
    end : str
        End data to get from, format yyyy-mm-dd

    Returns
    ----------
    pd.DataFrame
        Series data
    """
    df = pd.DataFrame()

    try:
        fredapi_client = Fred(cfg.API_FRED_KEY)
        df = fredapi_client.get_series(series_id, start, end)
    # Series does not exist & invalid api keys
    except HTTPError as e:
        console.print(e)

    return df


@log_start_end(log=logger)
def get_aggregated_series_data(
    d_series: Dict[str, Dict[str, str]], start: str = None, end: str = None
) -> pd.DataFrame:
    """Get Series data. [Source: FRED]
    Parameters
    ----------
    series_id : str
        Series ID to get data from
    start : str
        Start date to get data from, format yyyy-mm-dd
    end : str
        End data to get from, format yyyy-mm-dd

    Returns
    ----------
    pd.DataFrame
        Series data
    """
    series_ids = list(d_series.keys())
    data = pd.DataFrame()

    for s_id in series_ids:
        data = pd.concat(
            [
                data,
                pd.DataFrame(get_series_data(s_id, start, end), columns=[s_id]),
            ],
            axis=1,
        )

    return data


@log_start_end(log=logger)
def get_yield_curve(date: Optional[datetime]) -> Tuple[pd.DataFrame, str]:
    """Gets yield curve data from FRED

    Parameters
    ----------
    date: Optional[datetime]
        Date to get curve for.  If None, gets most recent date

    Returns
    -------
    pd.DataFrame:
        Dataframe of yields and maturities
    str
        Date for which the yield curve is obtained
    """
    fredapi_client = Fred(cfg.API_FRED_KEY)
    fred_series = {
        "1Month": "DGS1MO",
        "3Month": "DGS3MO",
        "6Month": "DGS6MO",
        "1Year": "DGS1",
        "2Year": "DGS2",
        "3Year": "DGS3",
        "5Year": "DGS5",
        "7Year": "DGS7",
        "10Year": "DGS10",
        "20Year": "DGS20",
        "30Year": "DGS30",
    }
    df = pd.DataFrame()

    if date is None:
        date_to_get = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    else:
        date_to_get = date.strftime("%Y-%m-%d")

    for key, s_id in fred_series.items():
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    fredapi_client.get_series(s_id, date_to_get), columns=[key]
                ),
            ],
            axis=1,
        )

    if date is None:
        date_of_yield = df.index[-1]
        rates = pd.DataFrame(df.iloc[-1, :].values, columns=["Rate"])
    else:
        date_of_yield = date
        series = df[df.index == date]
        if series.empty:
            return pd.DataFrame(), date.strftime("%Y-%m-%d")
        rates = pd.DataFrame(series.values.T, columns=["Rate"])

    rates["Maturity"] = [1 / 12, 1 / 4, 1 / 2, 1, 2, 3, 5, 7, 10, 20, 30]
    return rates, date_of_yield
