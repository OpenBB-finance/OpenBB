""" OECD model """
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from openbb_terminal.decorators import console, log_start_end

logger = logging.getLogger(__name__)

# pylint: disable=C0302

COUNTRY_TO_CODE_GDP = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "euro_area": "EA",
    "european_union": "EU",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "poland": "POL",
    "portugal": "PRT",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "south_africa": "ZAF",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}

COUNTRY_TO_CODE_RGDP = {
    "G20": "G-20",
    "G7": "G-7",
    "argentina": "ARG",
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "bulgaria": "BGR",
    "canada": "CAN",
    "chile": "CHL",
    "china": "CHN",
    "colombia": "COL",
    "costa_rica": "CRI",
    "croatia": "HRV",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "euro_area_19": "EA19",
    "europe": "OECDE",
    "european_union_27": "EU27_2020",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "india": "IND",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "oecd_total": "OECD",
    "poland": "POL",
    "portugal": "PRT",
    "romania": "ROU",
    "russia": "RUS",
    "saudi_arabia": "SAU",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "south_africa": "ZAF",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}

COUNTRY_TO_CODE_GDP_FORECAST = {
    "argentina": "ARG",
    "asia": "DAE",
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "bulgaria": "BGR",
    "canada": "CAN",
    "chile": "CHL",
    "china": "CHN",
    "colombia": "COL",
    "costa_rica": "CRI",
    "croatia": "HRV",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "euro_area_17": "EA17",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "india": "IND",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "non-oecd": "NMEC",
    "norway": "NOR",
    "oecd_total": "OECD",
    "peru": "PER",
    "poland": "POL",
    "portugal": "PRT",
    "romania": "ROU",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "south_africa": "ZAF",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
    "world": "WLD",
}

COUNTRY_TO_CODE_CPI = {
    "G20": "G-20",
    "G7": "G-7",
    "argentina": "ARG",
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "china": "CHN",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "euro_area_19": "EA19",
    "europe": "OECDE",
    "european_union_27": "EU27_2020",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "india": "IND",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "oecd_total": "OECD",
    "poland": "POL",
    "portugal": "PRT",
    "russia": "RUS",
    "saudi_arabia": "SAU",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "south_africa": "ZAF",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}

COUNTRY_TO_CODE_BALANCE = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "euro_area": "EA",
    "european_union": "EU",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "poland": "POL",
    "portugal": "PRT",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "south_africa": "ZAF",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}

COUNTRY_TO_CODE_REVENUE = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "euro_area": "EA",
    "european_union": "EU",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "oecd_average": "OAVG",
    "oecd_europe": "OEU",
    "oecd_total": "OECD",
    "poland": "POL",
    "portugal": "PRT",
    "romania": "ROU",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}

COUNTRY_TO_CODE_SPENDING = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "indonesia": "IDN",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "oecd_average": "OAVG",
    "oecd_europe": "OEU",
    "oecd_total": "OECD",
    "poland": "POL",
    "portugal": "PRT",
    "romania": "ROU",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}

COUNTRY_TO_CODE_DEBT = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "colombia": "COL",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "oecd_average": "OAVG",
    "oecd_total": "OECD",
    "poland": "POL",
    "portugal": "PRT",
    "romania": "ROU",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}

COUNTRY_TO_CODE_TRUST = {
    "australia": "AUS",
    "austria": "AUT",
    "belgium": "BEL",
    "brazil": "BRA",
    "canada": "CAN",
    "chile": "CHL",
    "colombia": "COL",
    "costa_rica": "CRI",
    "czech_republic": "CZE",
    "denmark": "DNK",
    "estonia": "EST",
    "finland": "FIN",
    "france": "FRA",
    "germany": "DEU",
    "greece": "GRC",
    "hungary": "HUN",
    "iceland": "ISL",
    "ireland": "IRL",
    "israel": "ISR",
    "italy": "ITA",
    "japan": "JPN",
    "korea": "KOR",
    "latvia": "LVA",
    "lithuania": "LTU",
    "luxembourg": "LUX",
    "mexico": "MEX",
    "netherlands": "NLD",
    "new_zealand": "NZL",
    "norway": "NOR",
    "poland": "POL",
    "portugal": "PRT",
    "russia": "RUS",
    "slovak_republic": "SVK",
    "slovenia": "SVN",
    "south_africa": "ZAF",
    "spain": "ESP",
    "sweden": "SWE",
    "switzerland": "CHE",
    "turkey": "TUR",
    "united_kingdom": "GBR",
    "united_states": "USA",
}


def no_data_message(error: str):
    """Print message when no data available or error"""
    console.print(f"Error getting data from OECD: [red]{error}[/red]")


@log_start_end(log=logger)
def get_gdp(
    countries: Optional[str] = "united_states",
    units: str = "USD",
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    Gross domestic product (GDP) is the standard measure of the value added created
    through the production of goods and services in a country during a certain period.
    As such, it also measures the income earned from that production, or the total amount
    spent on final goods and services (less imports). While GDP is the single most important
    indicator to capture economic activity, it falls short of providing a suitable measure of
    people's material well-being for which alternative indicators may be more appropriate.
    This indicator is based on nominal GDP (also called GDP at current prices or GDP in value)
    and is available in different measures: US dollars and US dollars per capita (current PPPs).
    All OECD countries compile their data according to the 2008 System of National Accounts (SNA).
    This indicator is less suited for comparisons over time, as developments are not only caused
    by real growth, but also by changes in prices and PPPs. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    units: str
        Units to get data in. Either 'USD' or 'USD_CAP'.
        Default is US dollars per capita.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with gdp data
    """
    if not start_date:
        start_date = datetime.now() - relativedelta(years=30)
    if not end_date:
        end_date = datetime.now()

    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    units_dict = {"USD": "MLN_USD", "USD_CAP": "USD_CAP"}

    if units not in units_dict:
        console.print(
            "Invalid choice, choices are either USD or USD_CAP. Defaulting to USD."
        )
        units = "USD"

    countries = [countries] if isinstance(countries, str) else countries  # type: ignore[assignment]

    df = pd.DataFrame()

    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.GDP.TOT.{units_dict[units]}.A/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_GDP[country]]["Value"]
            )
            temp.index = temp.index.map(str)
            temp.columns = [country]
            result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    result.index = pd.to_datetime(result.index, format="%Y")
    result.sort_index(inplace=True)
    result = result * 1000000 if units == "USD" else result

    return result


@log_start_end(log=logger)
def get_real_gdp(
    countries: Optional[List[str]],
    units: str = "PC_CHGPY",
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    Gross domestic product (GDP) is the standard measure of the value added
    created through the production of goods and services in a country during
    a certain period. As such, it also measures the income earned from that
    production, or the total amount spent on final goods and services (less imports).
    While GDP is the single most important indicator to capture economic activity, it
    falls short of providing a suitable measure of people's material well-being for
    which alternative indicators may be more appropriate. This indicator is based on
    real GDP (also called GDP at constant prices or GDP in volume), i.e. the developments
    over time are adjusted for price changes. The numbers are also adjusted for seasonal
    influences. The indicator is available in different measures: percentage change from
    the previous quarter, percentage change from the same quarter of the previous year and
    volume index (2015=100). All OECD countries compile their data according to the 2008
    System of National Accounts (SNA). [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    units: str
        Units to get data in. Either 'PC_CHGPP', 'PC_CHGPY' or 'IDX.
        Default is percentage change from the same quarter of the previous year.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with the gdp data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=10)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = datetime.now().date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    if units not in ["PC_CHGPP", "PC_CHGPY", "IDX"]:
        return console.print(
            "Use either PC_CHGPP (percentage change previous quarter), "
            "PC_CHGPY (percentage change from the same quarter of the "
            "previous year) or IDX (index with base at 2015) "
            "for units"
        )

    df = pd.DataFrame()

    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.QGDP."
            f"{'VOLIDX' if units == 'IDX' else 'TOT'}.{units}.Q/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_RGDP[country]]["Value"]
            )
            temp.index = temp.index.map(str)
            temp.columns = [country]
            result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    result.index = (
        pd.PeriodIndex(result.index, freq="Q").to_timestamp().strftime("%Y-%m")
    )
    result.sort_index(inplace=True)

    return result


@log_start_end(log=logger)
def get_gdp_forecast(
    countries: Optional[List[str]],
    types: str = "real",
    units: str = "Q",
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    Real gross domestic product (GDP) is GDP given in constant prices and
    refers to the volume level of GDP. Constant price estimates of GDP are
    obtained by expressing values of all goods and services produced in a
    given year, expressed in terms of a base period. Forecast is based on an
    assessment of the economic climate in individual countries and the world economy,
    using a combination of model-based analyses and expert judgement. This indicator
    is measured in growth rates compared to previous year. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    type: str
        Type of GDP to get data for. Either 'real' or 'nominal'.
        Default s real GDP (real).
    units: str
        Units to get data in. Either 'Q' or 'A.
        Default is Quarterly (Q).
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with the gdp data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=10)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = (datetime.now() + relativedelta(years=10)).date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    if units not in ["Q", "A"]:
        return console.print("Use either Q (quarterly) or A (annually) for units")
    if types not in ["real", "nominal"]:
        return console.print("Use either 'real' or 'nominal' for type")

    df = pd.DataFrame()

    try:
        if types == "real":
            df = pd.read_csv(
                f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.REALGDPFORECAST.TOT.AGRWTH.{units}/OECD?contentType=csv&detail=code"
                f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
                index_col=5,
            )
        else:
            df = pd.read_csv(
                f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.NOMGDPFORECAST.TOT.AGRWTH.{units}/OECD?contentType=csv&detail=code"
                f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
                index_col=5,
            )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_GDP_FORECAST[country]]["Value"]
            )
            temp.index = temp.index.map(str)
            temp.columns = [country]

            if temp.empty:
                console.print(f"No {types} GDP data for {country} with {units}.")
            else:
                result = pd.concat([result, temp], axis=1)

        except KeyError:
            console.print(f"No data available for {country}.")

    if units == "Q":
        result.index = (
            pd.PeriodIndex(result.index, freq="Q").to_timestamp().strftime("%Y-%m")
        )
        result.index = pd.to_datetime(result.index, format="%Y-%m")
    else:
        result.index = pd.to_datetime(result.index, format="%Y")

    result.sort_index(inplace=True)

    return result


@log_start_end(log=logger)
def get_debt(
    countries: Optional[List[str]],
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    General government debt-to-GDP ratio measures the gross debt of the general
    government as a percentage of GDP. It is a key indicator for the sustainability
    of government finance. Debt is calculated as the sum of the following liability
    categories (as applicable): currency and deposits; debt securities, loans; insurance,
    pensions and standardised guarantee schemes, and other accounts payable. Changes in
    government debt over time primarily reflect the impact of past government deficits. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with the debt data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=30)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = datetime.now().date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    df = pd.DataFrame()

    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.GGDEBT.TOT.PC_GDP.A/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_DEBT[country]]["Value"]
            )
            temp.index = temp.index.map(str)
            temp.columns = [country]
            result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    result.index = pd.to_datetime(result.index, format="%Y")
    result.sort_index(inplace=True)

    return result


@log_start_end(log=logger)
def get_cpi(
    countries: Optional[List[str]],
    perspective: str = "TOT",
    frequency: str = "Q",
    units: str = "AGRWTH",
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    Inflation measured by consumer price index (CPI) is defined as the change in the prices
    of a basket of goods and services that are typically purchased by specific groups of
    households. Inflation is measured in terms of the annual growth rate and in index,
    2015 base year with a breakdown for food, energy and total excluding food and energy.
    Inflation measures the erosion of living standards. A consumer price index is estimated
    as a series of summary measures of the period-to-period proportional change in the
    prices of a fixed set of consumer goods and services of constant quantity and
    characteristics, acquired, used or paid for by the reference population. Each summary
    measure is constructed as a weighted average of a large number of elementary aggregate indices.
    Each of the elementary aggregate indices is estimated using a sample of prices for a defined
    set of goods and services obtained in, or by residents of, a specific region from a given
    set of outlets or other sources of consumption goods and services. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    perspective: str
        Perspective of CPI you wish to obtain. This can be ENRG (energy), FOOD (food),
        TOT (total) or TOT_FOODENRG (total excluding food and energy)
        Default is Total CPI.
    frequency: str
        Frequency to get data in. Either 'M', 'Q' or 'A.
        Default is Quarterly (Q).
    units: str
        Units to get data in. Either 'AGRWTH' (annual growth rate) or IDX2015 (base = 2015).
        Default is Annual Growth Rate (AGRWTH).
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with cpi data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=5)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = datetime.now().date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    if perspective not in ["ENRG", "FOOD", "TOT", "TOT_FOODENRG"]:
        return console.print(
            "Use either ENRG (energy), FOOD (food), "
            "TOT (total) or TOT_FOODENRG (total excluding food and energy) for perspective"
        )
    if frequency not in ["M", "Q", "A"]:
        return console.print(
            "Use either M, (monthly), Q (quarterly) or A (annually) for frequency"
        )
    if units not in ["AGRWTH", "IDX2015"]:
        return console.print("Use either 'AGRWTH' or 'IDX2015' for type")

    df = pd.DataFrame()
    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.CPI.{perspective}.{units}.{frequency}/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_CPI[country]]["Value"]
            )
            temp.index = temp.index.map(str)
            temp.columns = [country]

            if temp.empty:
                console.print(
                    f"No {perspective} CPI data available for "
                    f"{country.title()} with set parameters."
                )
            else:
                result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    if frequency in ["M", "Q"]:
        result.index = pd.to_datetime(result.index).strftime("%Y-%m")
        result.index = pd.to_datetime(result.index, format="%Y-%m")
    else:
        result.index = pd.to_datetime(result.index, format="%Y")

    result.sort_index(inplace=True)

    return result


@log_start_end(log=logger)
def get_balance(
    countries: Optional[List[str]],
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    General government deficit is defined as the balance of income and expenditure of government,
    including capital income and capital expenditures. "Net lending" means that governmen
    has a surplus, and is providing financial resources to other sectors, while
    "net borrowing" means that government has a deficit, and requires financial
    esources from other sectors. This indicator is measured as a percentage of GDP.
    All OECD countries compile their data according to the
    2008 System of National Accounts (SNA 2008). [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with the balance data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=30)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = datetime.now().date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    df = pd.DataFrame()
    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.GGNLEND.TOT.PC_GDP.A/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_BALANCE[country]]["Value"]
            )
            temp.index = temp.index.map(str)
            temp.columns = [country]
            result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    result.index = pd.to_datetime(result.index, format="%Y")
    result.sort_index(inplace=True)

    return result


@log_start_end(log=logger)
def get_revenue(
    countries: Optional[List[str]],
    units: str = "PC_GDP",
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    Governments collect revenues mainly for two purposes: to finance the goods
    and services they provide to citizens and businesses, and to fulfil their
    redistributive role. Comparing levels of government revenues across
    countries provides an indication of the importance of the government
    sector in the economy in terms of available financial resources.
    The total amount of revenues collected by governments is determined
    by past and current political decisions. This indicator is measured
    in terms of thousand USD per capita, and as a percentage of GDP. All
    OECD countries compile their data according to the 2008 System of
    National Accounts (SNA 2008). [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    units: str
        Units to get data in. Either 'PC_GDP' or 'THOUSAND_USD_PER_CAPITA'.
        Default is Percentage of GDP.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with revenue data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=30)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = datetime.now().date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    if units not in ["THND_USD_CAP", "PC_GDP"]:
        return console.print(
            "Use either THND_USD_CAP (thousands of USD per capity) "
            "or PC_GDP (percentage of GDP) for units"
        )

    df = pd.DataFrame()
    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.GGREV.TOT.{units}.A/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_REVENUE[country]]["Value"]
            )

            temp.index = temp.index.map(str)
            temp.columns = [country]
            result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    result.index = pd.to_datetime(result.index, format="%Y")
    result.sort_index(inplace=True)

    return result


@log_start_end(log=logger)
def get_spending(
    countries: Optional[List[str]],
    perspective: str = "TOT",
    units: str = "PC_GDP",
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    General government spending provides an indication of the size
    of government across countries. The large variation in this indicator
    highlights the variety of countries' approaches to delivering public
    goods and services and providing social protection, not necessarily
    differences in resources spent. This indicator is measured in terms of
    thousand USD per capita, and as percentage of GDP. All OECD countries
    compile their data according to the 2008 System of
    National Accounts (SNA).[ Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    perspective: str
        The type of spending. Choose form the following:
            TOT (Total)
            RECULTREL (Recreation, culture and religion)
            HOUCOMM (Housing and community amenities)
            PUBORD (Public order and safety)
            EDU (Education)
            ENVPROT (Environmental protection)
            GRALPUBSER (General public services)
            SOCPROT (Social protection)
            ECOAFF (Economic affairs)
            DEF (Defence)
            HEALTH (Health)
    units: str
        Units to get data in. Either 'PC_GDP' or 'THOUSAND_USD_PER_CAPITA'.
        Default is Percentage of GDP.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with the spending data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=30)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = datetime.now().date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    if units not in ["THND_USD_CAP", "PC_GDP"]:
        console.print(
            "Use either THND_USD_CAP (thousands of USD per capity) "
            "or PC_GDP (percentage of GDP) for units"
        )
        return pd.DataFrame()
    if perspective not in [
        "TOT",
        "RECULTREL",
        "HOUCOMM",
        "PUBORD",
        "EDU",
        "ENVPROT",
        "GRALPUBSER",
        "SOCPROT",
        "ECOAFF",
        "DEF",
        "HEALTH",
    ]:
        console.print(
            "Use either TOT (Total),  RECULTREL (Recreation, culture and religion), "
            "HOUCOMM (Housing and community amenities), PUBORD (Public order and safety), "
            "EDU (Education), ENVPROT (Environmental protection), GRALPUBSER (General public services), "
            "SOCPROT (Social protection), ECOAFF (Economic affairs), DEF (Defence), HEALTH (Health)"
        )

    df = pd.DataFrame()
    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.GGEXP.{perspective}.{units}.A/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_SPENDING[country]]["Value"]
            )

            temp.index = temp.index.map(str)
            temp.columns = [country]
            result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    result.index = pd.to_datetime(result.index, format="%Y")
    result.sort_index(inplace=True)

    return result


@log_start_end(log=logger)
def get_trust(
    countries: Optional[List[str]],
    start_date="",
    end_date="",
) -> pd.DataFrame:
    """
    Trust in government refers to the share of people who report having confidence in
    the national government. The data shown reflect the share of respondents answering
    “yes” (the other response categories being “no”, and “don’t know”) to the
    survey question: “In this country, do you have confidence in… national
    government? Due to small sample sizes, country averages for horizontal inequalities
    (by age, gender and education) are pooled between 2010-18 to improve the accuracy
    of the estimates. The sample is ex ante designed to be nationally representative of
    the population aged 15 and over. This indicator is measured as a percentage
    of all survey respondents.  [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format

    Returns
    -------
    pd.DataFrame
        Dataframe with the trust data
    """
    if not start_date:
        start_date = (datetime.now() - relativedelta(years=30)).date()
    elif isinstance(start_date, datetime):
        start_date = start_date.date()
    if not end_date:
        end_date = datetime.now().date()
    elif isinstance(end_date, datetime):
        end_date = end_date.date()

    df = pd.DataFrame()
    try:
        df = pd.read_csv(
            f"https://stats.oecd.org/sdmx-json/data/DP_LIVE/.TRUSTGOV.TOT.PC.A/OECD?contentType=csv&detail=code"
            f"&separator=comma&csv-lang=en&startPeriod={start_date}&endPeriod={end_date}",
            index_col=5,
        )
    except Exception as e:
        no_data_message(error=str(e))
        return df

    df = df.iloc[:, [0, 5]]

    result = pd.DataFrame()
    for country in countries:  # type: ignore
        try:
            temp = pd.DataFrame(
                df[df["LOCATION"] == COUNTRY_TO_CODE_TRUST[country]]["Value"]
            )

            temp.index = temp.index.map(str)
            temp.columns = [country]
            result = pd.concat([result, temp], axis=1)
        except KeyError:
            console.print(f"No data available for {country}.")

    result.index = pd.to_datetime(result.index, format="%Y")
    result.sort_index(inplace=True)

    return result
