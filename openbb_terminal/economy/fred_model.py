""" Fred Model """
__docformat__ = "numpy"

import os
import logging
import textwrap
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from requests import HTTPError


import fred
import pandas as pd
import requests
from fredapi import Fred
import certifi

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def check_series_id(series_id: str) -> Tuple[bool, dict]:
    """Checks if series ID exists in fred

    Parameters
    ----------
    series_id: str
        Series ID to check

    Returns
    -------
    Tuple[bool, Dict]
        Boolean if series ID exists,
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
@check_api_key(["API_FRED_KEY"])
def get_series_notes(search_query: str, limit: int = -1) -> pd.DataFrame:
    """Get series notes. [Source: FRED]

    Parameters
    ----------
    search_query : str
        Text query to search on fred series notes database
    limit : int
        Maximum number of series notes to display

    Returns
    -------
    pd.DataFrame
        DataFrame of matched series
    """

    fred.key(cfg.API_FRED_KEY)
    d_series = fred.search(search_query)

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

        if "notes" in df_fred.columns:
            df_fred["notes"] = df_fred["notes"].apply(
                lambda x: "\n".join(textwrap.wrap(x, width=100))
                if isinstance(x, str)
                else x
            )
        if "title" in df_fred.columns:
            df_fred["title"] = df_fred["title"].apply(
                lambda x: "\n".join(textwrap.wrap(x, width=50))
                if isinstance(x, str)
                else x
            )

        if limit != -1:
            df_fred = df_fred[:limit]

    return df_fred


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_series_ids(search_query: str, limit: int = -1) -> pd.DataFrame:
    """Get Series IDs. [Source: FRED]

    Parameters
    ----------
    search_query : str
        Text query to search on fred series notes database
    limit : int
        Maximum number of series IDs to output

    Returns
    -------
    pd.Dataframe
        Dataframe with series IDs and titles
    """
    fred.key(cfg.API_FRED_KEY)
    d_series = fred.search(search_query)

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
    df_series = df_series.sort_values(by=["popularity"], ascending=False)
    if limit != -1:
        df_series = df_series.head(limit)
    df_series = df_series[["id", "title"]]
    df_series.set_index("id", inplace=True)

    return df_series


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_series_data(
    series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """Get Series data. [Source: FRED]

    Parameters
    ----------
    series_id : str
        Series ID to get data from
    start_date : Optional[str]
        Start date to get data from, format yyyy-mm-dd
    end_date : Optional[str]
        End data to get from, format yyyy-mm-dd

    Returns
    -------
    pd.DataFrame
        Series data
    """
    df = pd.DataFrame()

    try:
        # Necessary for installer so that it can locate the correct certificates for
        # API calls and https
        # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
        os.environ["SSL_CERT_FILE"] = certifi.where()
        fredapi_client = Fred(cfg.API_FRED_KEY)
        df = fredapi_client.get_series(series_id, start_date, end_date)
    # Series does not exist & invalid api keys
    except HTTPError as e:
        console.print(e)

    return df


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_aggregated_series_data(
    series_ids: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[pd.DataFrame, dict]:
    """Get Series data. [Source: FRED]

    Parameters
    ----------
    series_ids : List[str]
        Series ID to get data from
    start_date : str
        Start date to get data from, format yyyy-mm-dd
    end_date : str
        End data to get from, format yyyy-mm-dd

    Returns
    -------
    pd.DataFrame
        Series data
    dict
        Dictionary of series ids and titles
    """

    data = pd.DataFrame()

    detail = {}
    for ids in series_ids:
        information = check_series_id(ids)

        if "seriess" in information:
            detail[ids] = {
                "title": information["seriess"][0]["title"],
                "units": information["seriess"][0]["units_short"],
            }

    for s_id in series_ids:

        series = pd.DataFrame(
            get_series_data(s_id, start_date, end_date), columns=[s_id]
        ).dropna()

        data[s_id] = series[s_id]

    return data, detail


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def get_yield_curve(
    date: str = None,
) -> Tuple[pd.DataFrame, str]:
    """Gets yield curve data from FRED

    Parameters
    ----------
    date: str
        Date to get curve for. If None, gets most recent date (format yyyy-mm-dd)

    Returns
    -------
    Tuple[pd.DataFrame, str]
        Dataframe of yields and maturities,
        Date for which the yield curve is obtained

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> ycrv_df = openbb.economy.ycrv()
    """

    # Necessary for installer so that it can locate the correct certificates for
    # API calls and https
    # https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error/73270162#73270162
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    # os.environ["SSL_CERT_FILE"] = certifi.where()

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
        date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    for key, s_id in fred_series.items():
        df = pd.concat(
            [
                df,
                pd.DataFrame(fredapi_client.get_series(s_id, date), columns=[key]),
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
            return pd.DataFrame(), date_of_yield
        rates = pd.DataFrame(series.values.T, columns=["Rate"])

    rates.insert(
        0,
        "Maturity",
        [1 / 12, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30],
    )

    return rates, date_of_yield
