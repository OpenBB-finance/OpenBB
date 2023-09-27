"""NASDAQ Data Link Model"""
__docformat__ = "numpy"

import argparse
import logging
import pathlib
from datetime import datetime as dt
from typing import List, Optional, Union

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

NASDAQ_COUNTRY_CODES_PATH = (
    pathlib.Path(__file__).parent / "datasets" / "NASDAQ_CountryCodes.csv"
)


@log_start_end(log=logger)
def get_economic_calendar(
    countries: Union[List[str], str] = "",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get economic calendar for countries between specified dates

    Parameters
    ----------
    countries : [List[str],str]
        List of countries to include in calendar.  Empty returns all
    start_date : Optional[str]
        Start date for calendar
    end_date : Optional[str]
        End date for calendar

    Returns
    -------
    pd.DataFrame
        Economic calendar

    Examples
    --------
    Get todays economic calendar for the United States
    >>> from openbb_terminal.sdk import openbb
    >>> calendar = openbb.economy.events("united_states")

    To get multiple countries for a given date, pass the same start and end date as well as
    a list of countries
    >>> calendars = openbb.economy.events(["united_states", "canada"], start_date="2022-11-18", end_date="2022-11-18")
    """

    if start_date is None:
        start_date = dt.now().strftime("%Y-%m-%d")

    if end_date is None:
        end_date = dt.now().strftime("%Y-%m-%d")

    if countries == "":
        countries = []
    if isinstance(countries, str):
        countries = [countries]

    countries = [country.replace("_", " ").title() for country in countries]

    if start_date == end_date:
        dates = [start_date]
    else:
        dates = (
            pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d").tolist()
        )
    calendar = pd.DataFrame()
    for date in dates:
        try:
            df = pd.DataFrame(
                request(
                    f"https://api.nasdaq.com/api/calendar/economicevents?date={date}",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
                    },
                ).json()["data"]["rows"]
            ).replace("&nbsp;", "-")
            df.loc[:, "Date"] = date
            calendar = pd.concat([calendar, df], axis=0)
        except TypeError:
            continue

    if calendar.empty:
        console.print("[red]No data found for date range.[/red]")
        return pd.DataFrame()

    calendar = calendar.rename(
        columns={
            "gmt": "Time (ET)",
            "country": "Country",
            "eventName": "Event",
            "actual": "Actual",
            "consensus": "Consensus",
            "previous": "Previous",
        }
    )

    calendar = calendar.drop(columns=["description"])
    if not countries:
        return calendar

    calendar = calendar[calendar["Country"].isin(countries)].reset_index(drop=True)
    if calendar.empty:
        console.print(f"[red]No data found for {', '.join(countries)}[/red]")
        return pd.DataFrame()
    return calendar


@log_start_end(log=logger)
def check_country_code_type(list_of_codes: str) -> List[str]:
    """Check that codes are valid for NASDAQ API"""
    nasdaq_codes = list(pd.read_csv(NASDAQ_COUNTRY_CODES_PATH)["Code"])
    valid_codes = [
        code.upper()
        for code in list_of_codes.split(",")
        if code.upper() in nasdaq_codes
    ]

    if valid_codes:
        return valid_codes
    raise argparse.ArgumentTypeError("No valid codes provided.")


@log_start_end(log=logger)
def get_country_codes() -> List[str]:
    """Get available country codes for Bigmac index

    Returns
    -------
    List[str]
        List of ISO-3 letter country codes.
    """
    file = NASDAQ_COUNTRY_CODES_PATH
    codes = pd.read_csv(file, index_col=0)
    return codes


@log_start_end(log=logger)
def get_country_names() -> List[str]:
    """Get available country names in Nasdaq API

    Returns
    -------
    List[str]
        List of country names.
    """
    file = NASDAQ_COUNTRY_CODES_PATH
    df = pd.read_csv(file, index_col=0)
    countries = df["Country"]
    countries_list = [x.lower().replace(" ", "_") for x in countries]
    return countries_list


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def get_big_mac_index(country_code: str = "USA") -> pd.DataFrame:
    """Get the Big Mac index calculated by the Economist

    Parameters
    ----------
    country_code : str
        ISO-3 letter country code to retrieve. Codes available through get_country_codes().

    Returns
    -------
    pd.DataFrame
        Dataframe with Big Mac index converted to USD equivalent.
    """
    URL = f"https://data.nasdaq.com/api/v3/datasets/ECONOMIST/BIGMAC_{country_code}"
    URL += f"?column_index=3&api_key={get_current_user().credentials.API_KEY_QUANDL}"
    try:
        r = request(URL)
    except Exception:
        console.print("[red]Error connecting to NASDAQ API[/red]\n")
        return pd.DataFrame()

    df = pd.DataFrame()

    if r.status_code == 200:
        response_json = r.json()
        df = pd.DataFrame(response_json["dataset"]["data"])
        df.columns = response_json["dataset"]["column_names"]
        df["Date"] = pd.to_datetime(df["Date"])

    else:
        console.print(r.text)

    return df


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def get_big_mac_indices(country_codes: Optional[List[str]] = None) -> pd.DataFrame:
    """Display Big Mac Index for given countries

    Parameters
    ----------
    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through economy.country_codes().

    Returns
    -------
    pd.DataFrame
        Dataframe with Big Mac indices converted to USD equivalent.
    """
    big_mac = pd.DataFrame()

    if country_codes is None:
        country_codes = ["USA"]

    dfs = []
    for country in country_codes:
        df1 = get_big_mac_index(country)
        if not df1.empty:
            df1 = df1.rename(columns={"dollar_price": country})
            df1 = df1.set_index("Date")
            dfs.append(df1)
    if dfs:
        big_mac = pd.concat(dfs, axis=1)
        big_mac = big_mac.reset_index()
        big_mac = big_mac.set_index("Date")

    return big_mac
