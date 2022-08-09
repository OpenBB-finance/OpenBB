"""NASDAQ Data Link Model"""
__docformat__ = "numpy"

import argparse
import logging
import os
from typing import List

import pandas as pd
import requests

from openbb_terminal.config_terminal import API_KEY_QUANDL
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def check_country_code_type(list_of_codes: str) -> List[str]:
    """Check that codes are valid for NASDAQ API"""
    nasdaq_codes = list(
        pd.read_csv(os.path.join(os.path.dirname(__file__), "NASDAQ_CountryCodes.csv"))[
            "Code"
        ]
    )
    valid_codes = []
    for code in list_of_codes.split(","):
        if code.upper() in nasdaq_codes:
            valid_codes.append(code.upper())
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
    file = os.path.join(os.path.dirname(__file__), "NASDAQ_CountryCodes.csv")
    codes = pd.read_csv(file, index_col=0)
    return codes


@log_start_end(log=logger)
def get_big_mac_index(country_code: str) -> pd.DataFrame:
    """Gets the Big Mac index calculated by the Economist

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
    URL += f"?column_index=3&api_key={API_KEY_QUANDL}"
    r = requests.get(URL)

    df = pd.DataFrame()

    if r.status_code == 200:
        response_json = r.json()
        df = pd.DataFrame(response_json["dataset"]["data"])
        df.columns = response_json["dataset"]["column_names"]
        df["Date"] = pd.to_datetime(df["Date"])

    # Wrong API Key
    elif r.status_code == 400:
        console.print(r.text)
    # Premium Feature
    elif r.status_code == 403:
        console.print(r.text)
    # Catching other exception
    elif r.status_code != 200:
        console.print(r.text)

    return df


@log_start_end(log=logger)
def get_big_mac_indices(country_codes: List[str]) -> pd.DataFrame:
    """Display Big Mac Index for given countries

    Parameters
    ----------
    country_codes : List[str]
        List of country codes (ISO-3 letter country code). Codes available through get_country_codes().

    Returns
    -------
    pd.DataFrame
        Dataframe with Big Mac indices converted to USD equivalent.
    """

    df_cols = ["Date"]
    df_cols.extend(country_codes)
    big_mac = pd.DataFrame(columns=df_cols)
    for country in country_codes:
        df1 = get_big_mac_index(country)
        if not df1.empty:
            big_mac[country] = df1["dollar_price"]
            big_mac["Date"] = df1["Date"]
    big_mac.set_index("Date", inplace=True)

    return big_mac
