"""AlphaVantage FX Model."""

import argparse
import logging
import os
from typing import Any, Dict, List

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_timezone, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def get_currency_list() -> List:
    """Load AV currency codes from a local file."""
    path = os.path.join(os.path.dirname(__file__), "data/av_forex_currencies.csv")
    return list(pd.read_csv(path)["currency code"])


CURRENCY_LIST = get_currency_list()


@log_start_end(log=logger)
def check_valid_forex_currency(symbol: str) -> str:
    """Check if given symbol is supported on alphavantage.

    Parameters
    ----------
    symbol : str
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
    if symbol.upper() in CURRENCY_LIST:
        return symbol.upper()

    raise argparse.ArgumentTypeError(
        f"{symbol.upper()} not found in alphavantage supported currency codes. "
    )


@log_start_end(log=logger)
def get_quote(to_symbol: str = "USD", from_symbol: str = "EUR") -> Dict[str, Any]:
    """Get current exchange rate quote from alpha vantage.

    Parameters
    ----------
    to_symbol : str
        To forex symbol
    from_symbol : str
        From forex symbol

    Returns
    -------
    Dict[str, Any]
        Dictionary of exchange rate
    """
    url = (
        "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"
        + f"&from_currency={from_symbol}"
        + f"&to_currency={to_symbol}"
        + f"&apikey={get_current_user().credentials.API_KEY_ALPHAVANTAGE}"
    )

    response = request(url)
    response_json = response.json()
    result = {}

    # If the returned data was unsuccessful
    if "Error Message" in response_json:
        console.print(response_json["Error Message"])
        logger.error(response_json["Error Message"])
    else:
        # check if json is empty
        if not response_json:
            console.print("No data found.\n")
        else:
            result = response_json

    return result


@log_start_end(log=logger)
def get_historical(
    to_symbol: str = "USD",
    from_symbol: str = "EUR",
    resolution: str = "d",
    interval: int = 5,
    start_date: str = "",
    end_date: str = "",
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
    end_date : str, optional
        End date for data.

    Returns
    -------
    pd.DataFrame
        Historical data for forex pair
    """
    d_res = {"i": "FX_INTRADAY", "d": "FX_DAILY", "w": "FX_WEEKLY", "m": "FX_MONTHLY"}

    url = f"https://www.alphavantage.co/query?function={d_res[resolution]}&from_symbol={from_symbol}"
    url += f"&to_symbol={to_symbol}&outputsize=full&apikey={get_current_user().credentials.API_KEY_ALPHAVANTAGE}"
    if resolution == "i":
        url += f"&interval={interval}min"

    r = request(url)
    response_json = r.json()

    if r.status_code != 200:
        return pd.DataFrame()

    df = pd.DataFrame()

    # If the returned data was unsuccessful
    if "Error Message" in response_json:
        console.print(response_json["Error Message"])
    elif "Note" in response_json:
        console.print(response_json["Note"])
    else:
        # check if json is empty
        if not response_json:
            console.print("No data found.\n")
        else:
            if "Meta Data" not in response_json and "Information" in response_json:
                console.print(response_json["Information"])
                return pd.DataFrame()

            key = list(response_json.keys())[1]

            df = pd.DataFrame.from_dict(response_json[key], orient="index")
            df.index = pd.to_datetime(df.index)

            if start_date and resolution != "i":
                df = df[df.index > start_date]

            if end_date and resolution != "i":
                df = df[df.index < end_date]

            if (df.index.hour != 0).any():
                # if intraday data, convert to local timezone
                df.index = df.index.tz_localize("UTC").tz_convert(get_user_timezone())

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
