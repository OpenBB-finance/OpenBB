"""Blockchain Center Model"""
import json
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request, str_date_to_timestamp

logger = logging.getLogger(__name__)

DAYS = [30, 90, 365]


@log_start_end(log=logger)
def get_altcoin_index(
    period: int = 30,
    start_date: str = "2010-01-01",
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get altcoin index overtime
    [Source: https://blockchaincenter.net]

    Parameters
    ----------
    period: int
        Number of days {30,90,365} to check performance of coins and calculate the altcoin index.
        E.g., 365 checks yearly performance, 90 will check seasonal performance (90 days),
        30 will check monthly performance (30 days).
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Date, Value (Altcoin Index)
    """

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if period not in DAYS:
        return pd.DataFrame()
    soup = BeautifulSoup(
        request(
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

    ts_start_date = str_date_to_timestamp(start_date)
    ts_end_date = str_date_to_timestamp(end_date)

    df = df[
        (df.index > datetime.fromtimestamp(ts_start_date))
        & (df.index < datetime.fromtimestamp(ts_end_date))
    ]

    return df
