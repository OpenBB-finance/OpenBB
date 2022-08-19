"""Nasdaq Model"""
__docformat__ = "numpy"

import requests
import pandas as pd

from openbb_terminal.rich_config import console


def get_full_chain(symbol: str) -> pd.DataFrame:
    """

    Parameters
    ----------
    symbol: str
        Symbol to get options for.  Can be a stock, etf or index.

    Returns
    -------
    pd.DataFrame
        Dataframe of option chain
    """
    for asset in ["stocks", "index", "etf"]:
        url = (
            f"https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass={asset}&"
            "fromdate=2010-09-09&todate=2030-09-09&excode=oprac&callput=callput&money=at&type=all"
        )
        response_json = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
            },
        ).json()
        if response_json["status"]["rCode"] == 200:
            return pd.DataFrame(response_json["data"]["table"]["rows"])

    console.print(f"[red]{symbol} Option Chain not found.[/red]\n")
    return pd.DataFrame()
