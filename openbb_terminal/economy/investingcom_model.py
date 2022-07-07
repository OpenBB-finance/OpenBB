""" Investing.com Model """
__docformat__ = "numpy"

import logging
import argparse

import datetime
from time import time
import pandas as pd
import math
import pytz
import investpy

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import log_and_raise
from openbb_terminal import helper_funcs
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

COUNTRIES = investpy.bonds.get_bond_countries()
CATEGORIES = [
    "Employment",
    "Credit",
    "Balance",
    "Economic Activity",
    "Central Banks",
    "Bonds",
    "Inflation",
    "Confidence Index",
]
IMPORTANCES = ["high", "medium", "low"]


def check_correct_country(country):
    """Argparse type to check that correct country is inserted"""
    if country not in investpy.bonds.get_bond_countries():
        log_and_raise(
            argparse.ArgumentTypeError(
                f"{country} is an invalid country. Choose from {', '.join(investpy.bonds.get_bond_countries())}"
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
    return


@log_start_end(log=logger)
def get_economic_calendar(
    time_zone=None,
    countries=None,
    importances=None,
    categories=None,
    from_date=None,
    to_date=None,
) -> pd.DataFrame:
    """Get economic calendar [Source: Investing.com]

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

    if to_date:
        to_date = format_date(to_date)
    elif from_date:
        to_date = format_date(from_date + datetime.timedelta(days=7))
    else:
        to_date = format_date(datetime.date.today() + datetime.timedelta(days=7))

    if from_date:
        from_date = format_date(from_date)
    else:
        from_date = format_date(datetime.date.today())

    # Get user time zone in GMT offset format
    user_time_zone = pytz.timezone(helper_funcs.get_user_timezone())
    diff = pd.Timestamp.now(tz=user_time_zone).tz_localize(
        None
    ) - pd.Timestamp.utcnow().tz_localize(None)

    # Ceil time difference, might have actual decimal difference between .now() and .utcnow()
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
            from_date,
            to_date,
        )
    except:
        time_zone = None
        data = investpy.news.economic_calendar(
            time_zone,
            time_filter,
            countries,
            importances,
            categories,
            from_date,
            to_date,
        )

    if not data.empty:
        data.drop(columns=data.columns[0], axis=1, inplace=True)
        data.sort_values(by="date", inplace=True)
        data.drop_duplicates(keep="first", inplace=True)

    return data, time_zone
