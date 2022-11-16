"""Nasdaq Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.op_helpers import get_dte_from_expiration as get_dte

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation


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
        response_json = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            df = pd.DataFrame(response_json["data"]["table"]["rows"]).drop(
                columns=["c_colour", "p_colour", "drillDownURL"]
            )
            df["expirygroup"] = (
                df["expirygroup"].replace("", np.nan).fillna(method="ffill")
            )
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

            df = (
                df.fillna(np.nan)
                .dropna(axis=0)
                .replace("--", 0)
                .astype(columns_w_types)
            )
            df["DTE"] = df["expirygroup"].apply(lambda t: get_dte(t))
            df = df[df.DTE > 0]
            df = df.drop(columns=["DTE"])
            return df

    console.print(f"[red]{symbol} Option Chain not found.[/red]\n")
    return pd.DataFrame()


@log_start_end(log=logger)
def get_expirations(symbol: str) -> List[str]:
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
    exps = [exp for exp in list(df.expirygroup.unique()) if exp]
    # Convert 'January 11, 1993' into '1993-01-11'
    return [datetime.strptime(exp, "%B %d, %Y").strftime("%Y-%m-%d") for exp in exps]


@log_start_end(log=logger)
def get_chain_given_expiration(symbol: str, expiration: str) -> pd.DataFrame:
    """Get option chain for symbol at a given expiration

    Parameters
    ----------
    symbol: str
        Symbol to get chain for
    expiration: str
        Expiration to get chain for

    Returns
    -------
    pd.DataFrame
        Dataframe of option chain
    """
    for asset in ["stocks", "index", "etf"]:
        url = (
            f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset}&"
            f"fromdate={expiration}&todate={expiration}&excode=oprac&callput=callput&money=all&type=all"
        )

        response_json = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            df = (
                pd.DataFrame(
                    response_json.get("data", {}).get("table", {}).get("rows", {})
                )
                .drop(columns=["c_colour", "p_colour", "drillDownURL", "expirygroup"])
                .fillna(np.nan)
                .dropna(axis=0)
            )
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

            df = df.replace("--", 0).astype(columns_w_types)
            return df

    console.print(f"[red]{symbol} Option Chain not found.[/red]\n")
    return pd.DataFrame()


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
        response_json = requests.get(
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
        response_json = requests.get(
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
