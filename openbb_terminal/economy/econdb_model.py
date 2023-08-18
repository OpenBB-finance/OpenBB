""" EconDB Model """
__docformat__ = "numpy"

# pylint: disable=no-member

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Union
from urllib.error import HTTPError

import pandas as pd
import pandas_datareader.data as web
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.helpers_denomination import transform as transform_by_denomination
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

COUNTRY_CODES = {
    "Albania": "AL",
    "Argentina": "AR",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bangladesh": "BD",
    "Belarus": "BY",
    "Belgium": "BE",
    "Bhutan": "BT",
    "Bosnia_and_Herzegovina": "BA",
    "Botswana": "BW",
    "Brazil": "BR",
    "Bulgaria": "BG",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Chile": "CL",
    "China": "CN",
    "Colombia": "CO",
    "Croatia": "HR",
    "Cyprus": "CY",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Dominican_Republic": "DO",
    "Egypt": "EG",
    "Estonia": "EE",
    "European_Union": "EU",
    "Finland": "FI",
    "France": "FR",
    "Germany": "DE",
    "Greece": "GR",
    "Honduras": "HN",
    "Hong Kong": "HK",
    "Hungary": "HU",
    "India": "IN",
    "Indonesia": "ID",
    "Iran": "IR",
    "Ireland": "IE",
    "Israel": "IL",
    "Italy": "IT",
    "Japan": "JP",
    "Kazakhstan": "KZ",
    "Laos": "LA",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Macedonia": "MK",
    "Malaysia": "MY",
    "Malta": "MT",
    "Mexico": "MX",
    "Mongolia": "MN",
    "Netherlands": "NL",
    "New_Zealand": "NZ",
    "Nigeria": "NG",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Panama": "PA",
    "Paraguay": "PYG",
    "Peru": "PE",
    "Philippines": "PH",
    "Poland": "PL",
    "Portugal": "PT",
    "Qatar": "QA",
    "Romania": "RO",
    "Russia": "RU",
    "Saudi_Arabia": "SA",
    "Serbia": "RS",
    "Singapore": "SG",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "South_Africa": "ZA",
    "South_Korea": "KR",
    "Spain": "ES",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Taiwan": "TW",
    "Thailand": "TH",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Ukraine": "UA",
    "United_Arab_Emirates": "AE",
    "United_Kingdom": "UK",
    "United_States": "US",
    "Uzbekistan": "UZ",
    "Venezuela": "VE",
    "Vietnam": "VN",
}

COUNTRY_CURRENCIES = {
    "Albania": "ALL",
    "Argentina": "ARS",
    "Australia": "AUD",
    "Austria": "EUR",
    "Azerbaijan": "AZN",
    "Bangladesh": "BDT",
    "Belarus": "BYR",
    "Belgium": "EUR",
    "Bhutan": "BTN",
    "Bosnia_and_Herzegovina": "BAM",
    "Botswana": "BWP",
    "Brazil": "BRL",
    "Bulgaria": "BGN",
    "Cambodia": "KHR",
    "Cameroon": "XAF",
    "Canada": "CAD",
    "Chile": "CLP",
    "China": "CNY",
    "Colombia": "COP",
    "Croatia": "HRK",
    "Cyprus": "EUR",
    "Czechia": "CZK",
    "Denmark": "DKK",
    "Dominican_Republic": "DOP",
    "Egypt": "EGP",
    "Estonia": "EUR",
    "European_Union": "EUR",
    "Finland": "EUR",
    "France": "EUR",
    "Germany": "EUR",
    "Greece": "EUR",
    "Honduras": "HNL",
    "Hong Kong": "HKD",
    "Hungary": "HUF",
    "India": "INR",
    "Indonesia": "IDR",
    "Iran": "IRR",
    "Ireland": "EUR",
    "Israel": "ILS",
    "Italy": "EUR",
    "Japan": "JPY",
    "Kazakhstan": "KZT",
    "Laos": "LAK",
    "Latvia": "EUR",
    "Lebanon": "LBP",
    "Lithuania": "EUR",
    "Luxembourg": "EUR",
    "Macedonia": "MKD",
    "Malaysia": "MYR",
    "Malta": "EUR",
    "Mexico": "MXN",
    "Mongolia": "MNT",
    "Netherlands": "EUR",
    "New_Zealand": "NZD",
    "Nigeria": "NGN",
    "Norway": "NOK",
    "Oman": "OMR",
    "Pakistan": "PKR",
    "Panama": "PAB",
    "Paraguay": "PYG",
    "Peru": "PEN",
    "Philippines": "PHP",
    "Poland": "PLN",
    "Portugal": "EUR",
    "Qatar": "QAR",
    "Romania": "RON",
    "Russia": "RUB",
    "Saudi_Arabia": "SAR",
    "Serbia": "RSD",
    "Singapore": "SGD",
    "Slovakia": "EUR",
    "Slovenia": "EUR",
    "South_Africa": "ZAR",
    "South_Korea": "KRW",
    "Spain": "EUR",
    "Sweden": "SEK",
    "Switzerland": "CHF",
    "Taiwan": "TWD",
    "Thailand": "THB",
    "Tunisia": "TND",
    "Turkey": "TRY",
    "Ukraine": "UAH",
    "United_Arab_Emirates": "AED",
    "United_Kingdom": "GBP",
    "United_States": "USD",
    "Uzbekistan": "UZS",
    "Venezuela": "VEF",
    "Vietnam": "VND",
}

PARAMETERS = {
    "RGDP": {
        "name": "Real gross domestic product",
        "period": "Quarterly",
        "description": "Inflation-adjusted measure that reflects the value of all goods and services produced by "
        "an economy in a given year (chain-linked series).",
    },
    "RPRC": {
        "name": "Real private consumption",
        "period": "Quarterly",
        "description": "All purchases made by consumers adjusted by inflation (chain-linked series).",
    },
    "RPUC": {
        "name": "Real public consumption",
        "period": "Quarterly",
        "description": "All purchases made by the government adjusted by inflation (chain-linked series).",
    },
    "RGFCF": {
        "name": "Real gross fixed capital formation",
        "period": "Quarterly",
        "description": "The acquisition of produced assets adjusted by inflation (chain-linked series).",
    },
    "REXP": {
        "name": "Real exports of goods and services",
        "period": "Quarterly",
        "description": "Transactions in goods and services from residents to non-residents adjusted for "
        "inflation (chain-linked series)",
    },
    "RIMP": {
        "name": "Real imports of goods and services",
        "period": "Quarterly",
        "description": "Transactions in goods and services to residents from non-residents adjusted for "
        "inflation (chain-linked series)",
    },
    "GDP": {
        "name": "Gross domestic product",
        "period": "Quarterly",
        "description": "Measure that reflects the value of all goods and services produced by "
        "an economy in a given year (chain-linked series).",
    },
    "PRC": {
        "name": "Private consumption",
        "period": "Quarterly",
        "description": "All purchases made by consumers (chain-linked series).",
    },
    "PUC": {
        "name": "Public consumption",
        "period": "Quarterly",
        "description": "All purchases made by the government (chain-linked series)",
    },
    "GFCF": {
        "name": "Gross fixed capital formation",
        "period": "Quarterly",
        "description": "The acquisition of produced assets (chain-linked series).",
    },
    "EXP": {
        "name": "Exports of goods and services",
        "period": "Quarterly",
        "description": "Transactions in goods and services from residents to non-residents (chain-linked series)",
    },
    "IMP": {
        "name": "Imports of goods and services",
        "period": "Quarterly",
        "description": "Transactions in goods and services to residents from non-residents (chain-linked series)",
    },
    "CPI": {
        "name": "Consumer price index",
        "period": "Monthly",
        "description": "Purchasing power defined with base 2015 for Europe with varying bases for others. See: "
        "https://www.econdb.com/main-indicators",
    },
    "PPI": {
        "name": "Producer price index",
        "period": "Monthly",
        "description": "Change in selling prices with base 2015 for Europe with varying bases for others. See: "
        "https://www.econdb.com/main-indicators",
    },
    "CORE": {
        "name": "Core consumer price index",
        "period": "Monthly",
        "description": "Purchasing power excluding food and energy defined with base 2015 for Europe with varying "
        "bases for others. See: https://www.econdb.com/main-indicators",
    },
    "URATE": {
        "name": "Unemployment",
        "period": "Monthly",
        "description": "Monthly average % of the working-age population that is unemployed.",
    },
    "EMP": {
        "name": "Employment",
        "period": "Quarterly",
        "description": "The employed population within a country (in thousands).",
    },
    "ACOIO": {
        "name": "Active population",
        "period": "Quarterly",
        "description": "The active population, unemployed and employed, in thousands.",
    },
    "EMRATIO": {
        "name": "Employment to working age population",
        "period": "Quarterly",
        "description": "Unlike the unemployment rate, the employment-to-population ratio includes unemployed "
        "people not looking for jobs.",
    },
    "RETA": {
        "name": "Retail trade",
        "period": "Monthly",
        "description": "Turnover of sales in wholesale and retail trade",
    },
    "CONF": {
        "name": "Consumer confidence index",
        "period": "Monthly",
        "description": "Measures how optimistic or pessimistic consumers are regarding their expected financial "
        "situation.",
    },
    "IP": {
        "name": "Industrial production",
        "period": "Monthly",
        "description": "Measures monthly changes in the price-adjusted output of industry.",
    },
    "CP": {
        "name": "Construction production",
        "period": "Monthly",
        "description": "Measures monthly changes in the price-adjusted output of construction.",
    },
    "GBAL": {
        "name": "Government balance",
        "period": "Quarterly",
        "description": "The government balance (or EMU balance) is the overall difference between government "
        "revenues and spending.",
    },
    "GREV": {
        "name": "General government total revenue",
        "period": "Quarterly",
        "description": "The total amount of revenues collected by governments is determined by past and "
        "current political decisions.",
    },
    "GSPE": {
        "name": "General government total expenditure",
        "period": "Quarterly",
        "description": "Total expenditure consists of total expense and the net acquisition of "
        "non-financial assets. ",
    },
    "GDEBT": {
        "name": "Government debt",
        "period": "Quarterly",
        "description": "The financial liabilities of the government.",
    },
    "CA": {
        "name": "Current account balance",
        "period": "Monthly",
        "description": "A record of a country's international transactions with the rest of the world",
    },
    "TB": {
        "name": "Trade balance",
        "period": "Monthly",
        "description": "The difference between the monetary value of a nation's exports and imports over a "
        "certain time period.",
    },
    "NIIP": {
        "name": "Net international investment position",
        "period": "Quarterly",
        "description": "Measures the gap between a nation's stock of foreign assets and a foreigner's stock "
        "of that nation's assets",
    },
    "IIPA": {
        "name": "Net international investment position (Assets)",
        "period": "Quarterly",
        "description": "A nation's stock of foreign assets.",
    },
    "IIPL": {
        "name": "Net international investment position (Liabilities)",
        "period": "Quarterly",
        "description": "A foreigner's stock of the nation's assets.",
    },
    "Y10YD": {
        "name": "Long term yield (10-year)",
        "period": "Monthly",
        "description": "The 10-year yield is used as a proxy for mortgage rates. It's also seen as a "
        "sign of investor sentiment about the country's economy.",
    },
    "M3YD": {
        "name": "3 month yield",
        "period": "Monthly",
        "description": "The yield received for investing in a government issued treasury security "
        "that has a maturity of 3 months",
    },
    "HOU": {
        "name": "House price index",
        "period": "Monthly",
        "description": "House price index defined with base 2015 for Europe with varying "
        "bases for others. See: https://www.econdb.com/main-indicators",
    },
    "OILPROD": {
        "name": "Oil production",
        "period": "Monthly",
        "description": "The amount of oil barrels produced per day in a month within a country.",
    },
    "POP": {
        "name": "Population",
        "period": "Monthly",
        "description": "The population of a country. This can be in thousands or, "
        "when relatively small, in actual units.",
    },
}

TRANSFORM = {
    "": "No transformation",
    "TPOP": "Total percentage change on period",
    "TOYA": "Total percentage since 1 year ago",
    "TUSD": "Level USD",
    "TPGP": "Percentage of GDP",
    "TNOR": "Start = 100",
}

SCALES = {
    "Thousands": 1_000,
    "Tens of thousands": 10_000,
    "Hundreds of thousands": 100_000,
    "Millions": 1_000_000,
    "Tens of millions": 10_000_000,
    "Hundreds of millions": 100_000_000,
    "Billions": 1_000_000_000,
    "Tens of billions": 10_000_000_000,
    "Units": 1,
}

TREASURIES: Dict = {
    "frequencies": {
        "annually": 203,
        "monthly": 129,
        "weekly": 21,
        "daily": 9,
    },
    "instruments": {
        "nominal": {
            "identifier": "TCMNOM",
            "maturities": {
                "1m": "1-month",
                "3m": "3-month",
                "6m": "6-month",
                "1y": "1-year",
                "2y": "2-year",
                "3y": "3-year",
                "5y": "5-year",
                "7y": "7-year",
                "10y": "10-year",
                "20y": "20-year",
                "30y": "30-year",
            },
        },
        "inflation": {
            "identifier": "TCMII",
            "maturities": {
                "5y": "5-year",
                "7y": "7-year",
                "10y": "10-year",
                "20y": "20-year",
                "30y": "30-year",
            },
        },
        "average": {
            "identifier": "LTAVG",
            "maturities": {
                "Longer than 10-year": "Longer than 10-year",
            },
        },
        "secondary": {
            "identifier": "TB",
            "maturities": {
                "4w": "4-week",
                "3m": "3-month",
                "6m": "6-month",
                "1y": "1-year",
            },
        },
    },
}


@log_start_end(log=logger)
def get_macro_data(
    parameter: str,
    country: str,
    transform: str = "",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = None,
    symbol: str = "",
) -> Tuple[pd.Series, Union[str, Any]]:
    """Query the EconDB database to find specific macro data about a company [Source: EconDB]

    Parameters
    ----------
    parameter: str
        The type of data you wish to display
    country : str
        the selected country
    transform : str
        select data transformation from:
            '' - no transformation
            'TPOP' - total percentage change on period,
            'TOYA' - total percentage since 1 year ago,
            'TUSD' - level USD,
            'TPGP' - Percentage of GDP,
            'TNOR' - Start = 100
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : Optional[str]
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    symbol : str
        In what currency you wish to convert all values.

    Returns
    -------
    Tuple[pd.Series, Union[str, Any]]
        A series with the requested macro data of the chosen country,
        The units of the macro data, e.g. 'Bbl/day" for oil.
    """

    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    df, units = pd.DataFrame(), ""
    country = country.replace("_", " ")
    country = country.title()
    country = country.replace(" ", "_")
    parameter = parameter.upper()

    if country not in COUNTRY_CODES:
        console.print(f"No data available for the country {country}.")
        return pd.Series(dtype=float), ""
    if parameter not in PARAMETERS:
        console.print(f"The parameter {parameter} is not an option for {country}.")
        return pd.Series(dtype=float), ""
    if transform not in TRANSFORM:
        console.print(f"The transform {transform} is not a valid option.")
        return pd.Series(dtype=float), ""

    country_code = COUNTRY_CODES[country]
    country_currency = COUNTRY_CURRENCIES[country]

    try:
        code = f"{parameter}{country_code}"
        if transform:
            code += f"~{transform}"

        r = request(f"https://www.econdb.com/series/context/?tickers={code}")
        res_json = r.json()
        if res_json:
            data = res_json[0]
            scale = data["td"]["scale"]
            units = data["td"]["units"]

            df = pd.DataFrame(data["dataarray"])

            if code not in df.columns:
                console.print(
                    f"No data available for {parameter} of {country} "
                    f"{f'with transform method {transform}' if transform else ''}"
                )
                return pd.DataFrame(), "NA/NA"

            df = df.set_index(pd.to_datetime(df["date"]))[code] * SCALES[scale]
            df = df.sort_index().dropna()

            # Since a percentage is done through differences, the first value is NaN
            if transform in ["TPOP", "TOYA"]:
                df = df.iloc[1:]

        if not res_json or df.empty:
            console.print(
                f"No data available for {parameter} ({PARAMETERS[parameter]['name']}) "
                f"of country {country.replace('_', ' ')}"
            )
            return pd.Series(dtype=float), ""

        if start_date or end_date:
            try:
                dt_start = pd.to_datetime(start_date)
                dt_end = pd.to_datetime(end_date)
                df = df.loc[dt_start:dt_end]
            except TypeError:
                console.print("[red]Invalid date sent. Format as YYYY-MM-DD[/red]\n")
                return pd.DataFrame(), "NA/NA"

        if (
            symbol
            and country_currency != symbol
            and units in COUNTRY_CURRENCIES.values()
        ):
            if units in COUNTRY_CURRENCIES.values():
                units = symbol

            currency_data = yf.download(
                f"{country_currency}{symbol}=X",
                start=df.index[0],
                end=df.index[-1],
                progress=False,
            )["Adj Close"]

            merged_df = pd.merge_asof(
                df, currency_data, left_index=True, right_index=True
            )
            df = merged_df[code] * merged_df["Adj Close"]

            if pd.isna(df).any():
                df_old_oldest, df_old_newest = df.index[0].date(), df.index[-1].date()
                df = df.dropna()
                df_new_oldest, df_new_newest = df.index[0].date(), df.index[-1].date()
                console.print(
                    f"Due to missing exchange values, some data was dropped from {parameter} of {country}. "
                    f"Consider using the native currency if you want to prevent this. \n"
                    f"OLD: {df_old_oldest} - {df_old_newest}\n"
                    f"NEW: {df_new_oldest} - {df_new_newest}"
                )

        if not df.empty:
            df = df.groupby(df.index.strftime("%Y-%m")).head(1)
            df.index = df.index.strftime("%Y-%m")
            df = pd.to_numeric(df, errors="coerce").dropna()

    except HTTPError:
        return console.print(
            f"There is no data available for the combination {parameter} and {country}."
        )

    return df, units


@log_start_end(log=logger)
def get_macro_transform() -> Dict[str, str]:
    """This function returns the available macro transform with detail.

    Returns
    -------
    Dict[str, str]
        A dictionary with the available macro transforms.
    """
    return TRANSFORM


@log_start_end(log=logger)
def get_macro_parameters() -> Dict[str, Dict[str, str]]:
    """This function returns the available macro parameters with detail.

    Returns
    -------
    Dict[str, Dict[str, str]]
        A dictionary with the available macro parameters.
    """
    return PARAMETERS


@log_start_end(log=logger)
def get_macro_countries() -> Dict[str, str]:
    """This function returns the available countries and respective currencies.

    Returns
    -------
    Dict[str, str]
        A dictionary with the available countries and respective currencies.
    """
    return COUNTRY_CURRENCIES


@log_start_end(log=logger)
def get_aggregated_macro_data(
    parameters: Optional[list] = None,
    countries: Optional[list] = None,
    transform: str = "",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = None,
    symbol: str = "",
) -> Tuple[pd.DataFrame, Dict[Any, Dict[Any, Any]], str]:
    """This functions groups the data queried from the EconDB database [Source: EconDB]

    Parameters
    ----------
    parameters: list
        The type of data you wish to download. Available parameters can be accessed through economy.macro_parameters().
    countries : list
        The selected country or countries. Available countries can be accessed through economy.macro_countries().
    transform : str
        The selected transform. Available transforms can be accessed through get_macro_transform().
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : Optional[str]
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    symbol : str
        In what currency you wish to convert all values.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[Any, Dict[Any, Any]], str]
        A DataFrame with the requested macro data of all chosen countries,
        A dictionary containing the units of each country's parameter (e.g. EUR),
        A string denomination which can be Trillions, Billions, Millions, Thousands

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> macro_df = openbb.economy.macro()
    """

    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    if parameters is None:
        parameters = ["CPI"]
    if countries is None:
        countries = ["United_States"]

    country_data: Dict[Any, Dict[Any, pd.Series]] = {}
    units: Dict[Any, Dict[Any, Any]] = {}

    for country in countries:
        country_data[country] = {}
        units[country] = {}
        for parameter in parameters:
            (
                country_data[country][parameter],
                units[country][parameter],
            ) = get_macro_data(
                parameter, country, transform, start_date, end_date, symbol
            )

            if country_data[country][parameter].empty:
                del country_data[country][parameter]
                del units[country][parameter]

    country_data_df = (
        pd.DataFrame.from_dict(country_data, orient="index").stack().to_frame()
    )
    country_data_df = pd.DataFrame(
        country_data_df[0].values.tolist(), index=country_data_df.index
    ).T

    (df_rounded, denomination) = transform_by_denomination(country_data_df)
    df_rounded.index = pd.DatetimeIndex(df_rounded.index)

    if transform:
        denomination_string = f" [{TRANSFORM[transform]}]"
    else:
        denomination_string = f" [in {denomination}]" if denomination != "Units" else ""

    df_rounded = df_rounded.dropna()

    return (df_rounded, units, denomination_string)


@log_start_end(log=logger)
def get_treasuries(
    instruments: Optional[list] = None,
    maturities: Optional[list] = None,
    frequency: str = "monthly",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get U.S. Treasury rates [Source: EconDB]

    Parameters
    ----------
    instruments: list
        Type(s) of treasuries, nominal, inflation-adjusted (long term average) or secondary market.
        Available options can be accessed through economy.treasury_maturities().
    maturities : list
        Treasury maturities to get. Available options can be accessed through economy.treasury_maturities().
    frequency : str
        Frequency of the data, this can be annually, monthly, weekly or daily.
    start_date : str
        Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : Optional[str]
        End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.

    Returns
    -------
    treasury_data: pd.Dataframe
        Holds data of the selected types and maturities

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.economy.treasury()
    """

    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    if instruments is None:
        instruments = ["nominal"]
    if maturities is None:
        maturities = ["10y"]

    treasury_data: Dict[Any, Dict[Any, pd.Series]] = {}

    for instrument in instruments:
        if instrument not in TREASURIES["instruments"]:
            console.print(
                f"{instrument} is not an option. Please choose between: "
                f"{', '.join(TREASURIES['instruments'].keys())}"
            )
        else:
            instrument_identifier = TREASURIES["instruments"][instrument]["identifier"]
            frequency_number = TREASURIES["frequencies"][frequency]
            df = web.DataReader(
                "&".join(
                    [
                        "dataset=FRB_H15",
                        "v=Instrument",
                        "h=TIME",
                        f"instrument=[{instrument_identifier}]",
                        f"from={start_date}",
                        f"to={end_date}",
                        f"freq=[{frequency_number}",
                        "UNIT=[PERCENT:_PER_YEAR]",
                    ]
                ),
                "econdb",
            )

            if instrument == "average":
                maturities_list = ["Longer than 10-year"]
                type_string = "Long-term average"
            else:
                maturities_list = maturities
                type_string = instrument.capitalize()

            treasury_data[type_string] = {}

            for maturity in maturities_list:
                if maturity not in TREASURIES["instruments"][instrument]["maturities"]:
                    console.print(
                        f"The maturity {maturity} is not an option for {instrument}. Please choose between "
                        f"{', '.join(TREASURIES['instruments'][instrument]['maturities'].keys())}"
                    )
                else:
                    maturity_string = TREASURIES["instruments"][instrument][
                        "maturities"
                    ][maturity]

                    for column in df.columns:
                        # check if type inside the name and maturity inside the maturity string
                        if (
                            type_string.lower() in column[2].lower()
                            and maturity_string in column[3]
                        ):
                            treasury_data[type_string][maturity_string] = df[
                                column
                            ].dropna()
                            break

                    if maturity_string not in treasury_data[type_string]:
                        console.print(
                            f"No data found for the combination {instrument} and {maturity}."
                        )

    df = pd.DataFrame.from_dict(treasury_data, orient="index").stack().to_frame()
    df = pd.DataFrame(df[0].values.tolist(), index=df.index).T
    df.columns = ["_".join(column) for column in df.columns]

    return df


@log_start_end(log=logger)
def get_treasury_maturities() -> pd.DataFrame:
    """Get treasury maturity options [Source: EconDB]

    Returns
    -------
    df: pd.DataFrame
        Contains the name of the instruments and a string containing all options.
    """

    instrument_maturities = {
        instrument: ", ".join(values["maturities"].keys())
        for instrument, values in TREASURIES["instruments"].items()
    }

    df = pd.DataFrame.from_dict(instrument_maturities, orient="index")
    df.loc["average"] = "Defined by function"

    df.index.name = "Instrument"
    df.columns = ["Maturities"]

    return df
