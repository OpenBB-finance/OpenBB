"""NASDAQ Data Link Model"""
__docformat__ = "numpy"

import argparse
import os
from typing import List

import pandas as pd
import requests
from gamestonk_terminal.config_terminal import API_KEY_QUANDL


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


def get_big_mac_index(country_code: str) -> pd.DataFrame:
    """Gets the Big Mac index calculated by the Economist

    Parameters
    ----------
    country_code : str
        ISO-3 letter country code to retrieve

    Returns
    -------
    pd.DataFrame
        Dataframe with Big Mac index converted to USD equivalent.
    """
    r = requests.get(
        f"https://data.nasdaq.com/api/v3/datasets/ECONOMIST/BIGMAC_{country_code}?column_index=3&api_key={API_KEY_QUANDL}"
    )
    if r.status_code != 200:
        return pd.DataFrame()

    df = pd.DataFrame(r.json()["dataset"]["data"])
    df.columns = r.json()["dataset"]["column_names"]
    df["Date"] = pd.to_datetime(df["Date"])
    return df
