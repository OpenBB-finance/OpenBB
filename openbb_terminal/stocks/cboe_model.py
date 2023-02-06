"""CBOE Model Functions"""
__docformat__ = "numpy"

from typing import Tuple

import pandas as pd

from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console


def get_top_of_book(
    symbol: str, exchange: str = "BZX"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get top of book bid and ask for ticker on exchange [CBOE.com]

    Parameters
    ----------
    symbol: str
        Ticker to get
    exchange: str
        Exchange to look at.  Can be `BZX`,`EDGX`, `BYX`, `EDGA`

    Returns
    -------
    pd.DatatFrame
        Dataframe of Bids
    pd.DataFrame
        Dataframe of asks

    """
    if exchange not in ["BZX", "EDGX", "BYX", "EDGA"]:
        console.print(f"[red]Exchange not valid: {exchange}[/red]")
        return pd.DataFrame(), pd.DataFrame()
    # exchange need to be lower case.  Not sure why
    url = f"https://www.cboe.com/json/{exchange.lower()}/book/{symbol}"

    r = request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/106.0.0.0 Safari/537.36",
            "referer": "https://www.cboe.com/us/equities/market_statistics/book_viewer/",
        },
    )
    if r.status_code != 200:
        console.print(f"[red]Request failed with code {r.status_code}[/red]")
        return pd.DataFrame(), pd.DataFrame()
    r_json = r.json()
    if r_json["data"]["company"] == "unknown symbol":
        console.print(f"[red]Unknown symbol: {symbol}[/red]")
        return pd.DataFrame(), pd.DataFrame()
    bids = pd.DataFrame(r_json["data"]["bids"], columns=["Size", "Price"])
    asks = pd.DataFrame(r_json["data"]["asks"], columns=["Size", "Price"])
    if bids.empty or asks.empty:
        console.print(
            "[red]No bid/ask data. Note this is real time so there is no data after market close.[/red]"
        )
    return bids, asks
