"""Blockchain Center Model"""
import json
import logging
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)

DAYS = [30, 90, 365]


@log_start_end(log=logger)
def get_altcoin_index(period: int, since: int, until: int) -> pd.DataFrame:
    """Get altcoin index overtime
    [Source: https://blockchaincenter.net]

    Parameters
    ----------
    period: int
       Number of days {30,90,365} to check the performance of coins and calculate the altcoin index.
       E.g., 365 will check yearly performance (365 days), 90 will check seasonal performance (90 days),
       30 will check monthly performance (30 days).
    since : int
        Initial date timestamp (e.g., 1_609_459_200)
    until : int
        End date timestamp (e.g., 1_641_588_030)

    Returns
    -------
    pandas.DataFrame:
        Date, Value (Altcoin Index)
    """
    if period not in DAYS:
        return pd.DataFrame()
    soup = BeautifulSoup(
        requests.get(
            "https://www.blockchaincenter.net/altcoin-season-index/",
            headers={"User-Agent": get_user_agent()},
        ).content,
        "html.parser",
    )
    script = soup.select_one(f'script:-soup-contains("chartdata[{period}]")')

    string = script.contents[0].strip()
    initiator = string.index(f"chartdata[{period}] = ") + len(f"chartdata[{period}] = ")
    terminator = string.index(";")
    dict_data = json.loads(string[initiator:terminator])
    df = pd.DataFrame(
        zip(dict_data["labels"]["all"], dict_data["values"]["all"]),
        columns=("Date", "Value"),
    )
    df["Date"] = pd.to_datetime(df["Date"])
    df["Value"] = df["Value"].astype(int)
    df = df.set_index("Date")
    df = df[
        (df.index > datetime.fromtimestamp(since))
        & (df.index < datetime.fromtimestamp(until))
    ]

    return df
