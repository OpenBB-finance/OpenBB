"""Nasdaq Model"""
__docformat__ = "numpy"

from typing import Tuple, List

from datetime import datetime
import requests
import pandas as pd
import numpy as np

from openbb_terminal.rich_config import console


def get_full_chain(symbol: str) -> pd.DataFrame:
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
            df = (
                df.fillna(np.nan)
                .dropna(axis=0)
                .replace("--", 0)
                .astype(
                    {
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
                )
            )
            return df

    console.print(f"[red]{symbol} Option Chain not found.[/red]\n")
    return pd.DataFrame()


def get_expirations(symbol: str) -> List[str]:
    """Get available expirations

    Parameters
    ----------
    symbol

    Returns
    -------
    List[str]
        List of expiration dates
    """
    df = get_full_chain(symbol)
    if df.empty:
        return []
    # get everything that is not an empty string
    exps = [exp for exp in list(df.expirygroup.unique()) if exp]
    # Convert 'January 11, 1993' into '1993-01-11'
    return [datetime.strptime(exp, "%B %d, %Y").strftime("%Y-%m-%d") for exp in exps]


def get_chain_given_expiration(symbol: str, expiration: str) -> pd.DataFrame:
    """Get option chain for symbol at a given expiration

    Parameters
    ----------
    symbol: str
        Symbol to get chain for
    expiration
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
                pd.DataFrame(response_json["data"]["table"]["rows"])
                .drop(columns=["c_colour", "p_colour", "drillDownURL", "expirygroup"])
                .fillna(np.nan)
                .dropna(axis=0)
            )
            # Make numeric
            df = df.replace("--", 0).astype(
                {
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
            )
            return df

    console.print(f"[red]{symbol} Option Chain not found.[/red]\n")
    return pd.DataFrame()


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
