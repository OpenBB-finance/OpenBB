""" EconDB Model """
__docformat__ = "numpy"

import logging
from urllib.error import HTTPError

import pandas as pd
import yfinance as yf

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
    "Czech_Republic": "CZ",
    "Denmark": "DK",
    "Dominican_Republic": "DO",
    "Egypt": "EG",
    "Estonia": "EE",
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
    "Czech_Republic": "CZK",
    "Denmark": "DKK",
    "Dominican_Republic": "DOP",
    "Egypt": "EGP",
    "Estonia": "EUR",
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
    "United_States": "USD",
    "Uzbekistan": "UZS",
    "Venezuela": "VEF",
    "Vietnam": "VND",
}

PARAMETERS = {
    "RGDP": "Real gross domestic product",
    "RPRC": "Real private consumption",
    "RPUC": "Real public consumption",
    "RGFCF": "Real gross fixed capital formation",
    "REXP": "Real exports of goods and services",
    "RIMP": "Real imports of goods and services",
    "GDP": "Gross domestic product",
    "PRC": "Private consumption",
    "PUC": "Public consumption",
    "GFCF": "Gross fixed capital formation",
    "EXP": "Exports of goods and services",
    "IMP": "Imports of goods and services",
    "CPI": "Consumer price index",
    "PPI": "Producer price index",
    "CORE": "Core consumer price index",
    "URATE": "Unemployment",
    "EMP": "Employment",
    "ACOIO": "Active population",
    "EMRATIO": "Employment to working age population",
    "RETA": "Retail trade",
    "CONF": "Consumer confidence index",
    "IP": "Industrial production",
    "CP": "Construction production",
    "GBAL": "Government balance",
    "GREV": "General government total revenue",
    "GSPE": "General government total expenditure",
    "GDEBT": "Government debt",
    "CA": "Current account balance",
    "NIIP": "Net international investment position",
    "Y10YD": "Long term yield",
    "M3YD": "3 month yield",
    "HOU": "House price",
    "OILPROD": "Oil production",
    "POP": "Population",
}


@log_start_end(log=logger)
def get_data(parameter: str, country: str, convert_currency: str = "USD") -> pd.Series:
    """Query the EconDB database to find specific macro data about a company [Source: EconDB]

    Parameters
    ----------
    parameter: str
        The type of data you wish to acquire
    country : str
       the selected country
    convert_currency : bool
        The currency you wish to convert the data to.

    Returns
    ----------
    pd.Series
        A series with the requested macro data of the chosen country
    """
    if country not in COUNTRY_CODES:
        return console.print(f"No data available for the country {country}.")
    if parameter not in PARAMETERS:
        return console.print(f"The parameter {parameter} is not an option.")

    country_code = COUNTRY_CODES[country]
    country_currency = COUNTRY_CURRENCIES[country]

    try:
        df = pd.read_csv(
            f"https://www.econdb.com/api/series/{parameter}{country_code}/?format=csv",
            index_col="Date",
            parse_dates=["Date"],
            squeeze=True,
        )

        if convert_currency and country_currency != convert_currency:
            df = (
                df
                * yf.Ticker(f"{convert_currency}{country_currency}=X").history(
                    start=df.index[0]
                )["Close"][0]
            )

    except HTTPError:
        return console.print(
            f"There is no data available for the combination {parameter} and {country}."
        )

    if df.empty:
        return console.print(
            f"No data available for {parameter} ({PARAMETERS[parameter]}) "
            f"of country {country.replace('_', ' ')}"
        )

    return df
