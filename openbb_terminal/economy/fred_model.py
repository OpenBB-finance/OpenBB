""" Fred Model """
__docformat__ = "numpy"

import logging
import os
import pathlib
import textwrap
from typing import List, Optional, Tuple

import certifi
import fred
import pandas as pd
from fredapi import Fred
from requests import HTTPError

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

harmonized_cpi_path = pathlib.Path(__file__).parent / "datasets" / "harmonized_cpi.csv"
cpi_path = pathlib.Path(__file__).parent / "datasets" / "cpi.csv"

CPI_COUNTRIES = [
    "australia",
    "austria",
    "belgium",
    "brazil",
    "bulgaria",
    "canada",
    "chile",
    "china",
    "croatia",
    "cyprus",
    "czech_republic",
    "denmark",
    "estonia",
    "euro_area",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "iceland",
    "india",
    "indonesia",
    "ireland",
    "israel",
    "italy",
    "japan",
    "korea",
    "latvia",
    "lithuania",
    "luxembourg",
    "malta",
    "mexico",
    "netherlands",
    "new_zealand",
    "norway",
    "poland",
    "portugal",
    "romania",
    "russian_federation",
    "slovak_republic",
    "slovakia",
    "slovenia",
    "south_africa",
    "spain",
    "sweden",
    "switzerland",
    "turkey",
    "united_kingdom",
    "united_states",
]

CPI_UNITS = ["growth_previous", "growth_same", "index_2015"]

CPI_FREQUENCY = ["monthly", "quarterly", "annual"]


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
    r = request(url, headers={"User-Agent": get_user_agent()})
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
        return pd.DataFrame()

    if "seriess" not in d_series:
        return pd.DataFrame()

    if not d_series["seriess"]:
        return pd.DataFrame()

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
def get_cpi(
    countries: list,
    units: str = "",
    frequency: str = "",
    harmonized: bool = False,
    smart_select: bool = True,
    options: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Obtain CPI data from FRED. [Source: FRED]

    Parameters
    ----------
    countries: list
        The country or countries you want to see.
    units: str
        The units you want to see, can be "growth_previous", "growth_same" or "index_2015".
    frequency: str
        The frequency you want to see, either "annual", monthly" or "quarterly".
    harmonized: bool
        Whether you wish to obtain harmonized data.
    smart_select: bool
        Whether to assist with the selection.
    options: bool
        Whether to return the options.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    """
    series = pd.read_csv(harmonized_cpi_path) if harmonized else pd.read_csv(cpi_path)

    if options:
        return series.drop(["series_id"], axis=1)

    step_1 = series[series["country"].str.contains("|".join(countries))]
    step_2 = step_1[step_1["units"] == units]
    step_3 = step_2[step_2["frequency"] == frequency]

    if smart_select:
        if not step_3.empty and step_3["country"].nunique() == len(countries):
            series = step_3
        elif not step_2.empty and step_2["country"].nunique() == len(countries):
            console.print(
                f"No {frequency} data available for all countries. Using common frequency."
            )
            frequency_new = step_1["frequency"].mode()[0]
            series = step_2[step_2["frequency"] == frequency_new]
        else:
            console.print(
                f"No {frequency} and {units} data available for all countries. Using remaining options."
            )
            series = step_3 if not step_3.empty else step_2
    else:
        series = step_3

    if series.empty:
        console.print(
            "The combination of parameters does not result in any data. Please consider "
            "using the `options` parameter to see the available options. Note that there "
            "are two options list, one with `harmonized` and one without."
        )
        return pd.DataFrame()

    series_dictionary = {}

    for series_id, country_value, frequency_value, unit_value in series[
        ["series_id", "country", "frequency", "units"]
    ].values:
        series_dictionary[
            f"{country_value}-{frequency_value}-{unit_value}"
        ] = get_series_data(
            series_id=series_id, start_date=start_date, end_date=end_date
        )

    df = pd.DataFrame.from_dict(series_dictionary)
    df.index = pd.to_datetime(df.index).date

    return df
