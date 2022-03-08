"""AlphaVantage FX Model."""

import argparse
import logging
import os
from typing import Dict, List

import pandas as pd
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_currency_list() -> List:
    """Load AV currency codes from a local file."""
    path = os.path.join(os.path.dirname(__file__), "av_forex_currencies.csv")
    return list(pd.read_csv(path)["currency code"])


CURRENCY_LIST = get_currency_list()


@log_start_end(log=logger)
def check_valid_forex_currency(fx_symbol: str) -> str:
    """Check if given symbol is supported on alphavantage.

    Parameters
    ----------
    fx_symbol : str
        Symbol to check

    Returns
    -------
    str
        Currency symbol

    Raises
    ------
    argparse.ArgumentTypeError
        Symbol not valid on alphavantage
    """
    if fx_symbol.upper() in CURRENCY_LIST:
        return fx_symbol.upper()

    raise argparse.ArgumentTypeError(
        f"{fx_symbol.upper()} not found in alphavantage supported currency codes. "
    )


@log_start_end(log=logger)
def get_quote(to_symbol: str, from_symbol: str) -> Dict:
    """Get current exchange rate quote from alpha vantage.

    Parameters
    ----------
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol

    Returns
    -------
    Dict
        Dictionary of exchange rate
    """
    url = (
        "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"
        + f"&from_currency={from_symbol}"
        + f"&to_currency={to_symbol}"
        + f"&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    )

    response = requests.get(url)
    result = {}

    # If the returned data was unsuccessful
    if "Error Message" in response.json():
        console.print(response.json()["Error Message"])
        logger.error(response.json()["Error Message"])
    else:
        # check if json is empty
        if not response.json():
            console.print("No data found.\n")
        else:
            result = response.json()

    return result


@log_start_end(log=logger)
def get_historical(
    to_symbol: str,
    from_symbol: str,
    resolution: str = "d",
    interval: int = 5,
    start_date: str = "",
) -> pd.DataFrame:
    """Get historical forex data.

    Parameters
    ----------
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol
    resolution : str, optional
        Resolution of data.  Can be "i", "d", "w", "m" for intraday, daily, weekly or monthly
    interval : int, optional
        Interval for intraday data
    start_date : str, optional
        Start date for data.

    Returns
    -------
    pd.DataFrame
        Historical data for forex pair
    """
    d_res = {"i": "FX_INTRADAY", "d": "FX_DAILY", "w": "FX_WEEKLY", "m": "FX_MONTHLY"}

    url = f"https://www.alphavantage.co/query?function={d_res[resolution]}&from_symbol={from_symbol}"
    url += f"&to_symbol={to_symbol}&outputsize=full&apikey={cfg.API_KEY_ALPHAVANTAGE}"
    if resolution == "i":
        url += f"&interval={interval}min"

    r = requests.get(url)

    if r.status_code != 200:
        return pd.DataFrame()

    df = pd.DataFrame()

    # If the returned data was unsuccessful
    if "Error Message" in r.json():
        console.print(r.json()["Error Message"])
    else:
        # check if json is empty
        if not r.json():
            console.print("No data found.\n")
        else:
            key = list(r.json().keys())[1]

            df = pd.DataFrame.from_dict(r.json()[key], orient="index")

            if start_date and resolution != "i":
                df = df[df.index > start_date]

            df = df.rename(
                columns={
                    "1. open": "Open",
                    "2. high": "High",
                    "3. low": "Low",
                    "4. close": "Close",
                }
            )
            df.index = pd.DatetimeIndex(df.index)
            df = df[::-1]

    return df.astype(float)
