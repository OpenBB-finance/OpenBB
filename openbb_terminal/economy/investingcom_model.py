""" Investing.com Model """
__docformat__ = "numpy"

import logging
import argparse

import datetime
import math
from typing import Tuple
import pandas as pd

import pytz
import investpy

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import log_and_raise
from openbb_terminal import helper_funcs
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

BOND_COUNTRIES = investpy.bonds.get_bond_countries()
CALENDAR_COUNTRIES = list(investpy.utils.constant.COUNTRY_ID_FILTERS.keys()) + ["all"]
CATEGORIES = [
    "employment",
    "credit",
    "balance",
    "economic_activity",
    "central_banks",
    "bonds",
    "inflation",
    "confidence_index",
]
IMPORTANCES = ["high", "medium", "low", "all"]


@log_start_end(log=logger)
def get_ycrv_countries() -> list:
    """Get available countries for ycrv command.

    Returns:
        list: List of available countries.
    """
    return BOND_COUNTRIES


@log_start_end(log=logger)
def get_events_countries() -> list:
    """Get available countries for events command.

    Returns:
        list: List of available countries.
    """
    return CALENDAR_COUNTRIES


@log_start_end(log=logger)
def get_events_categories() -> list:
    """Get available event categories for events command.

    Returns:
        list: List of available event categories.
    """
    return CATEGORIES


@log_start_end(log=logger)
def check_correct_country(country: str, countries: list) -> str:
    """Check if country is in list and warn if not."""
    if country.lower() not in countries:
        log_and_raise(
            argparse.ArgumentTypeError(
                f"{country} is an invalid country. Choose from {', '.join(countries)}"
            )
        )
    return country


@log_start_end(log=logger)
def get_yieldcurve(country: str) -> pd.DataFrame:
    """Get yield curve for specified country. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country to display yield curve. List of available countries is accessible through get_ycrv_countries().

    Returns
    -------
    pd.DataFrame
        Country yield curve
    """

    if check_correct_country(country, BOND_COUNTRIES) != country:
        return pd.DataFrame()

    try:
        data = investpy.bonds.get_bonds_overview(country)
    except Exception:
        console.print(f"[red]Yield curve data not found for {country}.[/red]\n")
        return pd.DataFrame()

    data.drop(columns=data.columns[0], axis=1, inplace=True)
    data.rename(
        columns={
            "name": "Tenor",
            "last": "Current",
            "last_close": "Previous",
            "high": "High",
            "low": "Low",
            "change": "Change",
            "change_percentage": "% Change",
        },
        inplace=True,
    )

    data = data.replace(float("NaN"), "")

    for i, row in data.iterrows():
        t = row["Tenor"][-3:].strip()
        data.at[i, "Tenor"] = t
        if t[-1] == "M":
            data.at[i, "Tenor"] = int(t[:-1]) / 12
        elif t[-1] == "Y":
            data.at[i, "Tenor"] = int(t[:-1])

    return data


def format_date(date: datetime.date) -> str:
    year = str(date.year)
    if date.month < 10:
        month = "0" + str(date.month)
    else:
        month = str(date.month)
    if date.day < 10:
        day = "0" + str(date.day)
    else:
        day = str(date.day)

    return day + "/" + month + "/" + year


@log_start_end(log=logger)
def get_economic_calendar(
    country: str = "all",
    importance: str = "",
    category: str = "",
    start_date: datetime.date = None,
    end_date: datetime.date = None,
    limit=100,
) -> Tuple[pd.DataFrame, str]:
    """Get economic calendar [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country selected. List of available countries is accessible through get_events_countries().
    importance: str
        Importance selected from high, medium, low or all
    category: str
        Event category. List of available categories is accessible through get_events_categories().
    start_date: datetime.date
        First date to get events.
    end_date: datetime.date
        Last date to get events.

    Returns
    -------
    Tuple[pd.DataFrame, str]
        Economic calendar Dataframe and detail string about country/time zone.
    """

    if check_correct_country(country, CALENDAR_COUNTRIES) != country:
        return pd.DataFrame(), ""

    time_filter = "time_only"

    countries_list = []
    importances_list = []
    categories_list = []

    if country:
        countries_list = [country.lower()]
    if importance:
        importances_list = [importance.lower()]
    if category:
        categories_list = [category.title()]

    # Joint default for countries and importances
    if countries_list == ["all"] and not importances_list:
        countries_list = CALENDAR_COUNTRIES[:-1]
        importances_list = ["high"]
    elif importances_list is None:
        importances_list = ["all"]

    if start_date and not end_date:
        end_date_string = format_date(start_date + datetime.timedelta(days=7))
        start_date_string = format_date(start_date)
    elif end_date and not start_date:
        start_date_string = format_date(end_date + datetime.timedelta(days=-7))
        end_date_string = format_date(end_date)
    elif end_date and start_date:
        start_date_string = format_date(start_date)
        end_date_string = format_date(end_date)
    else:
        start_date_string = None
        end_date_string = None

    # Get user time zone in GMT offset format
    user_time_zone = pytz.timezone(helper_funcs.get_user_timezone())
    diff = pd.Timestamp.now(tz=user_time_zone).tz_localize(
        None
    ) - pd.Timestamp.utcnow().tz_localize(None)

    # Ceil time difference, might have actual decimal difference
    # between .now() and .utcnow()
    offset = divmod(math.ceil(diff.total_seconds()), 3600)[0]
    sign = "+" if offset > 0 else ""
    time_zone = "GMT " + sign + str(int(offset)) + ":00"

    try:
        data = investpy.news.economic_calendar(
            time_zone,
            time_filter,
            countries_list,
            importances_list,
            categories_list,
            start_date_string,
            end_date_string,
        )
    except Exception:
        data = investpy.news.economic_calendar(
            None,
            time_filter,
            countries_list,
            importances_list,
            categories_list,
            start_date_string,
            end_date_string,
        )

    if data.empty:
        logger.error("No data")
        console.print("[red]No data.[/red]\n")
        return pd.DataFrame(), ""

    data.drop(columns=data.columns[0], axis=1, inplace=True)
    data.drop_duplicates(keep="first", inplace=True)
    data["date"] = data["date"].apply(
        lambda date: date[-4:] + "-" + date[3:5] + "-" + date[:2]
    )
    data.sort_values(by=data.columns[0], inplace=True)

    if importances_list:
        if importances_list == ["all"]:
            importances_list = IMPORTANCES
        data = data[data["importance"].isin(importances_list)]

    if time_zone is None:
        time_zone = "GMT"
        console.print("[red]Error on timezone, default was used.[/red]\n")

    data.fillna(value="", inplace=True)
    data.columns = data.columns.str.title()
    if len(countries_list) == 1:
        del data["Zone"]
        detail = f"{country.title()} economic calendar ({time_zone})"
    else:
        detail = f"Economic Calendar ({time_zone})"
        data["Zone"] = data["Zone"].str.title()

    data["Importance"] = data["Importance"].str.title()

    data = data[:limit]

    return data, detail
