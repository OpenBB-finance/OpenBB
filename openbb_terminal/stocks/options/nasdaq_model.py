"""Nasdaq Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation

call_cols = [
    "c_Last",
    "c_Bid",
    "c_Ask",
    "c_Volume",
    "c_Openinterest",
    "strike",
    "expiration",
]
put_cols = [
    "p_Last",
    "p_Bid",
    "p_Ask",
    "p_Volume",
    "p_Openinterest",
    "strike",
    "expiration",
]
cols = ["lastPrice", "bid", "ask", "volume", "openInterest", "strike", "expiration"]

sorted_chain_columns = [
    "optionType",
    "expiration",
    "strike",
    "lastPrice",
    "bid",
    "ask",
    "openInterest",
    "volume",
]


def get_dte_from_expiration(date: str) -> float:
    """
    Converts a date to total days until the option would expire.
    This assumes that the date is in the form %B %d, %Y such as January 11, 2023
    This calculates time from 'now' to 4 PM the date of expiration
    This is particularly a helper for nasdaq results.

    Parameters
    ----------
    date: str
        Date in format %B %d, %Y

    Returns
    -------
    float
        Days to expiration as a decimal
    """
    # Get the date as a datetime and add 16 hours (4PM)
    expiration_time = datetime.strptime(date, "%B %d, %Y") + timedelta(hours=16)
    # Find total seconds from now
    time_to_now = (expiration_time - datetime.now()).total_seconds()
    # Convert to days
    time_to_now /= 60 * 60 * 24
    return time_to_now


@log_start_end(log=logger)
def get_full_option_chain(symbol: str) -> pd.DataFrame:
    """Get the full option chain for symbol over all expirations

    Parameters
    ----------
    symbol: str
        Symbol to get options for.  Can be a stock, etf or index.

    Returns
    -------
    pd.DataFrame
        Dataframe of option chain
    """
    # Nasdaq requires an asset code, so instead of making user supply one, just loop through all
    for asset in ["stocks", "index", "etf"]:
        url = (
            f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset}&"
            "fromdate=2010-09-09&todate=2030-09-09&excode=oprac&callput=callput&money=all&type=all"
        )
        # I have had issues with nasdaq requests, and this user agent seems to work in US and EU
        response_json = request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()

        if response_json["status"]["rCode"] == 200:
            return process_response(response_json)

    console.print(f"[red]{symbol} Option Chain not found.[/red]\n")
    return pd.DataFrame()


def process_response(response_json):
    df = pd.DataFrame(response_json["data"]["table"]["rows"]).drop(
        columns=["c_colour", "p_colour", "drillDownURL"]
    )
    df["expirygroup"] = df["expirygroup"].replace("", np.nan).fillna(method="ffill")
    df["expiration"] = pd.to_datetime(
        df["expirygroup"], format="%B %d, %Y"
    ).dt.strftime("%Y-%m-%d")
    # Make numeric
    columns_w_types = {
        "c_Last": float,
        "c_Change": float,
        "c_Bid": float,
        "c_Ask": float,
        "c_Volume": int,
        "c_Openinterest": int,
        "strike": float,
        "p_Last": float,
        "p_Change": float,
        "p_Bid": float,
        "p_Ask": float,
        "p_Volume": int,
        "p_Openinterest": int,
    }

    for key, _ in columns_w_types.items():
        df[key] = df[key].replace(",", "", regex=True)

    df = df.fillna(np.nan).dropna(axis=0).replace("--", 0).astype(columns_w_types)
    df["DTE"] = df["expirygroup"].apply(lambda t: get_dte_from_expiration(t))
    df = df[df.DTE > 0]
    df = df.drop(columns=["DTE"])

    # Process into consistent format
    calls = df[call_cols].copy()
    puts = df[put_cols].copy()

    calls.columns = cols
    puts.columns = cols
    calls["optionType"] = "call"
    puts["optionType"] = "put"

    chain = (
        pd.concat([calls, puts], axis=0)
        .sort_values(by=["expiration", "strike"])
        .reset_index(drop=True)
    )

    return chain[sorted_chain_columns]


@log_start_end(log=logger)
def option_expirations(symbol: str) -> List[str]:
    """Get available expirations

    Parameters
    ----------
    symbol : str
        Ticker symbol to get expirations for

    Returns
    -------
    List[str]
        List of expiration dates
    """
    df = get_full_option_chain(symbol)

    if df.empty:
        return []

    # get everything that is not an empty string
    return [exp for exp in list(df.expiration.unique()) if exp]


@log_start_end(log=logger)
def get_last_price(symbol: str) -> float:
    """Get the last price from nasdaq

    Parameters
    ----------
    symbol: str
        Symbol to get quote for

    Returns
    -------
    float
        Last price
    """
    for asset in ["stocks", "index", "etf"]:
        url = f"https://api.nasdaq.com/api/quote/{symbol}/info?assetclass={asset}"
        response_json = request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            return float(
                response_json["data"]["primaryData"]["lastSalePrice"]
                .strip("$")
                .replace(",", "")
            )
    console.print(f"[red]Last price for {symbol} not found[/red]\n")
    return np.nan


# Ugh this doesn't get the full chain
# TODO: apply CRR binomial tree to backtrack IV for greeks
@log_start_end(log=logger)
def get_option_greeks(symbol: str, expiration: str) -> pd.DataFrame:
    """Get option greeks from nasdaq

    Parameters
    ----------
    symbol: str
        Symbol to get
    expiration: str
        Option expiration

    Returns
    -------
    pd.DataFrame
        Dataframe with option greeks
    """
    for asset in ["stocks", "index", "etf"]:
        url_greeks = f"https://api.nasdaq.com/api/quote/{symbol}/option-chain/greeks?assetclass={asset}&date={expiration}"
        response_json = request(
            url_greeks,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            greeks = pd.DataFrame(response_json["data"]["table"]["rows"])
            greeks = greeks.drop(columns="url")
            return greeks

    console.print(f"[red]Greeks not found for {symbol} on {expiration}[/red].")
    return pd.DataFrame()
