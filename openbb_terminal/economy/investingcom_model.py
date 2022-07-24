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

logger = logging.getLogger(__name__)

COUNTRIES = investpy.bonds.get_bond_countries()
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


def check_correct_country(country):
    """Argparse type to check that correct country is inserted"""
    if country.lower() not in investpy.bonds.get_bond_countries():
        log_and_raise(
            argparse.ArgumentTypeError(
                f"{country} is an invalid country. Choose from \
                    {', '.join(investpy.bonds.get_bond_countries())}"
            )
        )
    return country


@log_start_end(log=logger)
def get_yieldcurve(country) -> pd.DataFrame:
    """Get country yield curve [Source: Investing.com]

    Returns
    -------
    pd.DataFrame
        Country yield curve
    """

    data = investpy.bonds.get_bonds_overview(country)
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
        today = datetime.date.today()
        from_date_string = format_date(today)
        to_date_string = format_date(today + datetime.timedelta(days=7))

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
        data.sort_values(by="date", inplace=True)
        data.drop_duplicates(keep="first", inplace=True)

        if importances:
            if importances == ["all"]:
                importances = IMPORTANCES
            data = data[data["importance"].isin(importances)]

    return data, time_zone
