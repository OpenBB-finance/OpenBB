""" EconDB Model """
__docformat__ = "numpy"

# pylint: disable=no-member

import logging
from typing import Dict, Any, Tuple, Union
from urllib.error import HTTPError
from datetime import datetime

import pandas as pd
import pandas_datareader.data as web
import requests
import yfinance as yf
from pandas import DataFrame

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

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
    "TBFR": {
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

SCALES = {
    "Thousands": 1_000,
    "Millions": 1_000_000,
    "Hundreds of millions": 100_000_000,
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
    start_date=pd.to_datetime("1900-01-01"),
    end_date=datetime.today().date(),
    convert_currency=False,
) -> Tuple[Any, Union[str, Any]]:
    """Query the EconDB database to find specific macro data about a company [Source: EconDB]

    Parameters
    ----------
    parameter: str
        The type of data you wish to acquire
    country : str
       the selected country
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    convert_currency : str
        In what currency you wish to convert all values.

    Returns
    ----------
    pd.Series
        A series with the requested macro data of the chosen country
    units
        The units of the macro data, e.g. 'Bbl/day" for oil.
    """
    country = country.replace(" ", "_")

    if country not in COUNTRY_CODES:
        console.print(f"No data available for the country {country}.")
        return pd.Series(), ""
    if parameter not in PARAMETERS:
        console.print(f"The parameter {parameter} is not an option for {country}.")
        return pd.Series(), ""

    country_code = COUNTRY_CODES[country]
    country_currency = COUNTRY_CURRENCIES[country]

    try:
        r = requests.get(
            f"https://www.econdb.com/series/context/?tickers={parameter}{country_code}"
        )
        data = r.json()[0]
        scale = data["td"]["scale"]
        units = data["td"]["units"]

        df = pd.DataFrame(data["dataarray"])
        df = (
            df.set_index(pd.to_datetime(df["date"]))[f"{parameter}{country_code}"]
            * SCALES[scale]
        )
        df = df.sort_index().dropna()

        if df.empty:
            console.print(
                f"No data available for {parameter} ({PARAMETERS[parameter]['name']}) "
                f"of country {country.replace('_', ' ')}"
            )
            return pd.Series(), ""

        if start_date or end_date:
            df = df.loc[start_date:end_date]

        if (
            convert_currency
            and country_currency != convert_currency
            and units in COUNTRY_CURRENCIES.values()
        ):
            if units in COUNTRY_CURRENCIES.values():
                units = convert_currency

            currency_data = yf.download(
                f"{country_currency}{convert_currency}=X",
                start=df.index[0],
                end=df.index[-1],
                progress=False,
            )["Adj Close"]

            merged_df = pd.merge_asof(
                df, currency_data, left_index=True, right_index=True
            )
            df = merged_df[f"{parameter}{country_code}"] * merged_df["Adj Close"]

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

    except HTTPError:
        return console.print(
            f"There is no data available for the combination {parameter} and {country}."
        )

    return df, units


@log_start_end(log=logger)
def get_aggregated_macro_data(
    parameters: list,
    countries: list,
    start_date: str = "1900-01-01",
    end_date=datetime.today().date(),
    convert_currency=False,
) -> Tuple[DataFrame, Dict[Any, Dict[Any, Any]]]:
    """This functions groups the data queried from the EconDB database [Source: EconDB]

    Parameters
    ----------
    parameters: list
        The type of data you wish to acquire
    countries : list
       the selected country or countries
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    convert_currency : str
        In what currency you wish to convert all values.

    Returns
    ----------
    pd.DataFrame
        A DataFrame with the requested macro data of all chosen countries
    Dictionary
        A dictionary containing the units of each country's parameter (e.g. EUR)
    """
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
                parameter, country, start_date, end_date, convert_currency
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

    return country_data_df, units


@log_start_end(log=logger)
def get_treasuries(
    instruments: list,
    maturities: list,
    frequency: str = "monthly",
    start_date: str = "1900-01-01",
    end_date=datetime.today().date(),
) -> Dict[Any, Dict[Any, pd.Series]]:
    """Obtain U.S. Treasury Rates [Source: EconDB]

    Parameters
    ----------
    instruments: list
        The type(s) of treasuries, nominal, inflation-adjusted (long term average) or secondary market.
    maturities : list
       the maturities you wish to view.
    frequency : str
        The frequency of the data, this can be annually, monthly, weekly or daily.
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.

    Returns
    ----------
    treasury_data: dict
        Holds data of the selected types and maturities
    """
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
                        if type_string in column[2] and maturity_string in column[3]:
                            treasury_data[type_string][maturity_string] = df[
                                column
                            ].dropna()
                            break

                    if maturity_string not in treasury_data[type_string]:
                        console.print(
                            f"No data found for the combination {instrument} and {maturity}."
                        )

    return treasury_data


@log_start_end(log=logger)
def obtain_treasury_maturities(treasuries: Dict) -> pd.DataFrame:
    """Obtain treasury maturity options [Source: EconDB]

    Parameters
    ----------
    treasuries: dict
        A dictionary containing the options structured {instrument : {maturities: {abbreviation : name}}}

    Returns
    ----------
    df: pd.DataFrame
        Contains the name of the instruments and a string containing all options.
    """

    instrument_maturities = {
        instrument: ", ".join(values["maturities"].keys())
        for instrument, values in treasuries["instruments"].items()
    }

    df = pd.DataFrame.from_dict(instrument_maturities, orient="index")
    df.loc["average"] = "Defined by function"

    return df
