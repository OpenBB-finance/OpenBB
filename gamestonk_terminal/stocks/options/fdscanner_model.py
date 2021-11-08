"""FDScanner model"""
__docformat__ = "numpy"

import numpy as np
import pandas as pd
import requests
from gamestonk_terminal.helper_funcs import get_user_agent


def unusual_options(num: int, sort_column: str, ascending: bool):
    """Get unusual option activity from fdscanner.com

    Parameters
    ----------
    num: int
        Number to show
    sort_column: str
        Column to sort data by
    ascending: bool
        Flag to sort by ascending

    Returns
    -------
    df: pd.DataFrame
        Dataframe containing options information
    last_updated: pd.Timestamp
        Timestamp indicated when data was updated from website
    """
    pages = np.arange(0, num // 20 + 1)
    data_list = []
    for page_num in pages:

        r = requests.get(
            f"https://app.fdscanner.com/api2/unusualvolume?p=0&page_size=20&page={int(page_num)}",
            headers={"User-Agent": get_user_agent()},
        )

        if r.status_code != 200:
            print("Error in fdscanner request")
            return pd.DataFrame(), "request error"

        data_list.append(r.json())

    ticker, expiry, option, ask, bid, oi, vol, voi = [], [], [], [], [], [], [], []
    for data in data_list:
        for entry in data["data"]:
            ticker.append(entry["tk"])
            expiry.append(entry["expiry"])
            option.append(str(entry["s"]) + " " + entry["t"])
            ask.append(entry["a"])
            bid.append(entry["b"])
            oi.append(entry["oi"])
            vol.append(entry["v"])
            voi.append(entry["vol/oi"])

    # Subtract an hour to align with NYSE timezone
    last_updated = pd.to_datetime(
        data_list[-1]["last_updated"], unit="s"
    ) - pd.Timedelta(hours=1)

    df = pd.DataFrame(
        {
            "Ticker": ticker,
            "Exp": expiry,
            "Option": option,
            "Vol/OI": voi,
            "Vol": vol,
            "OI": oi,
            "Bid": bid,
            "Ask": ask,
        }
    )
    df = df.sort_values(by=sort_column, ascending=ascending)

    return df, last_updated
