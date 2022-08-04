""" Investing.com Model """
__docformat__ = "numpy"

import logging
import argparse

import datetime
import math
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
    "economic activity",
    "central banks",
    "bonds",
    "inflation",
    "confidence index",
]
IMPORTANCES = ["high", "medium", "low", "all"]


@log_start_end(log=logger)
def get_ycrv_countries() -> list:
    """Get avaiable countries for ycrv command.

    Returns:
        list: List of available countries.
    """
    return BOND_COUNTRIES


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


@log_start_end(log=logger)
def get_economic_calendar(
    countries: list = None,
    importances: list = None,
    categories: list = None,
    from_date: datetime.date = None,
    to_date: datetime.date = None,
) -> pd.DataFrame:
    """Get economic calendar [Source: Investing.com]

    Parameters
    ----------
    countries: list
        Country selected from allowed list
    importances: list
        Importance selected from high, medium, low or all
    categories: list
        Event category. E.g. Employment, Inflation, among others
    from_date: datetime.date
        First date to get events if applicable
    to_date: datetime.date
        Last date to get events if applicable

    Returns
    -------
    pd.DataFrame
        Economic calendar
    """

    time_filter = "time_only"

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

    # Joint default for countries and importances
    if countries == ["all"] and importances == []:
        countries = CALENDAR_COUNTRIES[:-1]
        importances = ["high"]
    elif importances is None:
        importances = ["all"]

    if from_date and not to_date:
        to_date_string = format_date(from_date + datetime.timedelta(days=7))
        from_date_string = format_date(from_date)
    elif to_date and not from_date:
        from_date_string = format_date(to_date + datetime.timedelta(days=-7))
        to_date_string = format_date(to_date)
    elif to_date and from_date:
        from_date_string = format_date(from_date)
        to_date_string = format_date(to_date)
    else:
        from_date_string = None
        to_date_string = None

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
            countries,
            importances,
            categories,
            from_date_string,
            to_date_string,
        )
    except Exception:
        data = investpy.news.economic_calendar(
            None,
            time_filter,
            countries,
            importances,
            categories,
            from_date_string,
            to_date_string,
        )

    if not data.empty:
        data.drop(columns=data.columns[0], axis=1, inplace=True)
        data.drop_duplicates(keep="first", inplace=True)
        data["date"] = data["date"].apply(
            lambda date: date[-4:] + "-" + date[3:5] + "-" + date[:2]
        )
        data.sort_values(by=data.columns[0], inplace=True)

        if importances:
            if importances == ["all"]:
                importances = IMPORTANCES
            data = data[data["importance"].isin(importances)]

    return data, time_zone
