"""Tradier options model"""
__docformat__ = "numpy"

from typing import List, Optional

import pandas as pd
import requests

from gamestonk_terminal import config_terminal as cfg

option_columns = [
    "symbol",
    "bid",
    "ask",
    "strike",
    "bidsize",
    "asksize",
    "volume",
    "open_interest",
    "option_type",
]
greek_columns = ["delta", "gamma", "theta", "vega", "ask_iv", "bid_iv", "mid_iv"]
df_columns = option_columns + greek_columns

default_columns = [
    "mid_iv",
    "vega",
    "delta",
    "gamma",
    "theta",
    "volume",
    "open_interest",
    "bid",
    "ask",
]


def get_historical_options(
    ticker: str, expiry: str, strike: float, put: bool, chain_id: Optional[str]
) -> pd.DataFrame:
    """
    Gets historical option pricing.  This inputs either ticker, expiration, strike or the OCC chain ID and processes
    the request to tradier for historical premiums.

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        Option expiration date
    put: bool
        Is this a put option?
    chain_id: Optional[str]
        OCC chain ID

    Returns
    -------
    df_hist: pd.DataFrame
        Dataframe of historical option prices
    """
    if not chain_id:
        op_type = ["call", "put"][put]
        chain = get_option_chains(ticker, expiry)

        try:
            symbol = chain[(chain.strike == strike) & (chain.option_type == op_type)][
                "symbol"
            ].values[0]
        except IndexError:
            print(f"Strike: {strike}, Option type: {op_type} not not found \n")
            return pd.DataFrame
    else:
        symbol = chain_id

    response = requests.get(
        "https://sandbox.tradier.com/v1/markets/history",
        params={"symbol": {symbol}, "interval": "daily"},
        headers={
            "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
            "Accept": "application/json",
        },
    )

    if response.status_code != 200:
        print("Error with request")
        return pd.DataFrame()

    data = response.json()["history"]
    if not data:
        print("No historical data available")
        return pd.DataFrame()

    df_hist = pd.DataFrame(data["day"]).set_index("date")
    df_hist.index = pd.DatetimeIndex(df_hist.index)
    return df_hist


# pylint: disable=no-else-return


def option_expirations(ticker: str) -> List[str]:
    """Get available expiration dates for given ticker

    Parameters
    ----------
    ticker: str
        Ticker to get expirations for

    Returns
    -------
    dates: List[str]
        List of of available expirations
    """
    r = requests.get(
        "https://sandbox.tradier.com/v1/markets/options/expirations",
        params={"symbol": ticker, "includeAllRoots": "true", "strikes": "false"},
        headers={
            "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
            "Accept": "application/json",
        },
    )
    if r.status_code == 200:
        try:
            dates = r.json()["expirations"]["date"]
            return dates
        except TypeError:
            print("Error in tradier JSON response.  Check loaded ticker.\n")
            return []
    else:
        print("Tradier request failed.  Check token. \n")
        return []


def get_option_chains(symbol: str, expiry: str) -> pd.DataFrame:
    """Display option chains [Source: Tradier]"

    Parameters
    ----------
    symbol : str
        Ticker to get options for
    expiry : str
        Expiration date in the form of "YYYY-MM-DD"

    Returns
    -------
    chains: pd.DataFrame
        Dataframe with options for the given Symbol and Expiration date
    """
    params = {"symbol": symbol, "expiration": expiry, "greeks": "true"}

    headers = {
        "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
        "Accept": "application/json",
    }

    response = requests.get(
        "https://sandbox.tradier.com/v1/markets/options/chains",
        params=params,
        headers=headers,
    )
    if response.status_code != 200:
        print("Error in request. Check TRADIER_TOKEN\n")
        return pd.DataFrame()

    chains = process_chains(response)
    return chains


def process_chains(response: requests.models.Response) -> pd.DataFrame:
    """Function to take in the requests.get and return a DataFrame

    Parameters
    ----------
    response: requests.models.Response
        This is the response from tradier api.

    Returns
    -------
    opt_chain: pd.DataFrame
        Dataframe with all available options
    """
    json_response = response.json()
    options = json_response["options"]["option"]

    opt_chain = pd.DataFrame(columns=df_columns)
    for idx, option in enumerate(options):
        data = [option[col] for col in option_columns]
        data += [option["greeks"][col] for col in greek_columns]
        opt_chain.loc[idx, :] = data

    return opt_chain


def last_price(ticker: str):
    """Makes api request for last price

    Parameters
    ----------
    ticker: str
        Ticker

    Returns
    -------
    float:
        Last price
    """
    r = requests.get(
        "https://sandbox.tradier.com/v1/markets/quotes",
        params={"symbols": ticker, "includeAllRoots": "true", "strikes": "false"},
        headers={
            "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
            "Accept": "application/json",
        },
    )
    if r.status_code == 200:
        return float(r.json()["quotes"]["quote"]["last"])
    else:
        print("Error getting last price")
        return None
