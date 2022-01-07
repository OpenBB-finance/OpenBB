"""Blockchain Center Model"""
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

from gamestonk_terminal.helper_funcs import get_user_agent

DAYS = [30, 90, 365]


def get_altcoin_index(period: int, since: int, until: int) -> pd.DataFrame:
    """Get altcoin index overtime
     [Source: https://blockchaincenter.net]

     Parameters
     ----------
     days: int
        Number of days to check the performance of coins and calculate the altcoin index.
        E.g., 365 will check yearly performance (365 days), 90 will check seasonal performance (90 days),
        30 will check monthly performance (30 days).
     since : int
        Initial date timestamp (e.g., 1_614_556_800)
     until : int
        End date timestamp (e.g., 1_614_556_800)

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
        'html.parser',
    )
    script = soup.select_one(f'script:-soup-contains("chartdata[{period}]")')

    string = script.contents[0].strip()
    initiator = string.index(f'chartdata[{period}] = ') + len(f"chartdata[{period}] = ")
    terminator = string.index(';')
    dict_data = json.loads(string[initiator:terminator])
    df = pd.DataFrame(zip(dict_data["labels"]["all"], dict_data["values"]["all"]), columns=("Date", "Value"))
    df['Date'] = pd.to_datetime(df['Date'])
    df['Value'] = df['Value'].astype(int)
    df = df.set_index("Date")
    df = df[(df.index > datetime.fromtimestamp(1_601_596_800)) & (df.index < datetime.fromtimestamp(1_641_573_787))]

    return df
