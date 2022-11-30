""" Investing.com Model """
__docformat__ = "numpy"

import logging
import argparse

import datetime
import math
from typing import Dict, List, Tuple, Union
import pandas as pd

import pytz
import investpy
from tqdm import tqdm

from openbb_terminal.decorators import log_start_end
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

# Commented countries either have no data or are not correctly formatted in investpy itself
MATRIX_COUNTRIES = {
    "G7": [
        "United states",
        "Canada",
        "Japan",
        "Germany",
        "France",
        "Italy",
        "United Kingdom",
    ],
    "PIIGS": [
        "Portugal",
        "Italy",
        "Ireland",
        "Greece",
        "Spain",
    ],
    "EZ": [
        "Austria",
        "Belgium",
        "Cyprus",
        # "Estonia",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Ireland",
        "Italy",
        # "Latvia",
        # "Lithuania",
        # "Luxembourg",
        "Malta",
        "Netherlands",
        "Portugal",
        "Slovakia",
        "Slovenia",
        "Spain",
    ],
    "AMERICAS": [
        "Brazil",
        "Canada",
        "Chile",
        "Colombia",
        "Mexico",
        "Peru",
        "United states",
    ],
    "EUROPE": [
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        # "Czech Republic",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Hungary",
        "Iceland",
        "Ireland",
        "Italy",
        "Malta",
        "Netherlands",
        "Norway",
        "Poland",
        "Portugal",
        "Romania",
        "Russia",
        "Serbia",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Switzerland",
        "Turkey",
        # "Ukraine",
        "United Kingdom",
    ],
    "ME": [
        # "Bahrain",
        "Egypt",
        "Israel",
        "Jordan",
        "Qatar",
    ],
    "APAC": [
        "Australia",
        "Bangladesh",
        "China",
        # "Hong Kong",
        "India",
        "Indonesia",
        "Japan",
        # "Kazakhstan",
        "Malaysia",
        # "New Zealand",
        "Pakistan",
        "Philippines",
        "Singapore",
        # "South Korea",
        # "Sri Lanka",
        "Taiwan",
        "Vietnam",
    ],
    "AFRICA": [
        # "Botswana",
        "Kenya",
        "Mauritius",
        "Morocco",
        "Namibia",
        "Nigeria",
        # "South Africa",
        "Uganda",
    ],
}

MATRIX_CHOICES = list(MATRIX_COUNTRIES.keys())


@log_start_end(log=logger)
def check_correct_country(country: str, countries: list) -> bool:
    """Check if country is in list and warn if not."""
    if country.lower() not in countries:
        joined_countries = [x.replace(" ", "_").lower() for x in countries]
        choices = ", ".join(joined_countries)
        console.print(
            f"[red]'{country}' is an invalid country. Choose from {choices}[/red]\n"
        )
        return False
    return True


@log_start_end(log=logger)
def countries_string_to_list(countries_list: str) -> List[str]:
    """Transform countries string to list if countries valid

    Parameters
    ----------
    countries_list : str
        String of countries separated by commas

    Returns
    -------
    List[str]
        List of countries
    """
    valid_countries = [
        country.lower().strip()
        for country in countries_list.split(",")
        if check_correct_country(country.strip(), BOND_COUNTRIES)
    ]

    if valid_countries:
        return valid_countries
    raise argparse.ArgumentTypeError("No valid countries provided.")


@log_start_end(log=logger)
def create_matrix(dictionary: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Create matrix of yield and spreads.

    Parameters
    ----------
    dictionary: Dict[str, Dict[str, float]]
        Dictionary of yield data by country. E.g. {'10Y': {'United States': 4.009, 'Canada': 3.48}}

    Returns
    -------
    pd.DataFrame
        Spread matrix.
    """

    maturity = list(dictionary.keys())[0]
    d = dictionary[maturity]
    countries = list(d.keys())

    # Create empty matrix
    matrix: List[List[float]] = []
    N = len(d)
    for i in range(N):
        matrix.append([0] * N)

    for i, country_i in enumerate(countries):
        for j, country_j in enumerate(countries):
            matrix[i][j] = round((d[country_i] - d[country_j]) * 100, 1)

    matrixdf = pd.DataFrame(matrix)
    matrixdf.columns = list(d.keys())
    matrixdf = matrixdf.set_index(matrixdf.columns)
    matrixdf.insert(
        0, "Yield " + maturity, pd.DataFrame.from_dict(d, orient="index") * 100
    )

    return matrixdf


@log_start_end(log=logger)
def get_spread_matrix(
    countries: Union[str, List[str]] = "G7",
    maturity: str = "10Y",
    change: bool = False,
) -> pd.DataFrame:
    """Get spread matrix. [Source: Investing.com]

    Parameters
    ----------
    countries: Union[str, List[str]]
        Countries or group of countries. List of available countries is accessible through get_ycrv_countries().
    maturity: str
        Maturity to get data. By default 10Y.
    change: bool
        Flag to use 1 day change or not. By default False.

    Returns
    -------
    pd.DataFrame
        Spread matrix.
    """

    if isinstance(countries, str) and countries.upper() in MATRIX_CHOICES:
        countries = MATRIX_COUNTRIES[countries.upper()]

    d0: Dict[str, Dict[str, float]] = {maturity: {}}
    d1: Dict[str, Dict[str, float]] = {maturity: {}}
    no_data_countries = []
    for country in tqdm(countries, desc="Downloading"):
        country = country.title()
        try:
            df = investpy.bonds.get_bonds_overview(country)
            d0[maturity][country] = df[df["name"].str.contains(maturity)]["last"].iloc[
                0
            ]
            d1[maturity][country] = df[df["name"].str.contains(maturity)][
                "last_close"
            ].iloc[0]
        except Exception:
            no_data_countries.append(country)

    if no_data_countries:
        s = ", ".join(no_data_countries)
        console.print(f"[red]No data for {s}.[/red]")

    if change:
        return create_matrix(d0) - create_matrix(d1)
    return create_matrix(d0)


@log_start_end(log=logger)
def get_ycrv_countries() -> List[str]:
    """Get available countries for ycrv command.

    Returns
    -------
    List[str]
        List of available countries.
    """
    return BOND_COUNTRIES


@log_start_end(log=logger)
def get_events_countries() -> List[str]:
    """Get available countries for events command.

    Returns
    -------
    List[str]
        List of available countries.
    """
    return CALENDAR_COUNTRIES


@log_start_end(log=logger)
def get_events_categories() -> List[str]:
    """Get available event categories for events command.

    Returns
    -------
    List[str]
        List of available event categories.
    """
    return CATEGORIES


@log_start_end(log=logger)
def get_yieldcurve(country: str = "United States") -> pd.DataFrame:
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

    if not check_correct_country(country, BOND_COUNTRIES):
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

    data["Change"] = (data["Current"] - data["Previous"]) * 100

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
    start_date: str = "",
    end_date: str = "",
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

    if not check_correct_country(country, CALENDAR_COUNTRIES):
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
    if countries_list == ["all"]:
        countries_list = CALENDAR_COUNTRIES[:-1]
        if not importances_list:
            importances_list = ["high"]
    elif importances_list is None:
        importances_list = ["all"]

    if start_date and not end_date:
        end_date_string = (
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            + datetime.timedelta(days=7)
        ).strftime("%d/%m/%Y")
        start_date_string = (
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
        ).strftime("%d/%m/%Y")
    elif end_date and not start_date:
        start_date_string = (
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
            + datetime.timedelta(days=-7)
        ).strftime("%d/%m/%Y")
        end_date_string = (datetime.datetime.strptime(end_date, "%Y-%m-%d")).strftime(
            "%d/%m/%Y"
        )
    elif end_date and start_date:
        start_date_string = (
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
        ).strftime("%d/%m/%Y")
        end_date_string = (datetime.datetime.strptime(end_date, "%Y-%m-%d")).strftime(
            "%d/%m/%Y"
        )
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

    args = [
        time_filter,
        countries_list,
        importances_list,
        categories_list,
        start_date_string,
        end_date_string,
    ]
    try:
        data = investpy.news.economic_calendar(time_zone, *args)
    except Exception:
        try:
            data = investpy.news.economic_calendar(None, *args)
        except Exception:
            console.print(
                f"[red]Economic calendar data not found for {country}.[/red]\n"
            )
            return pd.DataFrame(), ""

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
