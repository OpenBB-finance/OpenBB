"""Utility for FINRA data storage.

This was created as a way to handle short interest data from the FINRA.
The files do not change, so there is no need to download them every time.
"""

import random
import sqlite3
from io import StringIO
from pathlib import Path
from typing import List

import requests
from openbb_core.app.utils import get_user_cache_directory
from openbb_finra.utils.helpers import get_short_interest_dates
from pandas import read_csv

DB_PATH = Path(get_user_cache_directory()) / "caches/finra_short_volume.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_cached_dates() -> List:
    """Return the dates that are cached in the DB file."""
    cnx = sqlite3.connect(DB_PATH)
    cursor = cnx.cursor()

    # Check if the table exists
    cursor.execute(
        "SELECT * FROM sqlite_master WHERE type='table' AND name='short_interest'"
    )
    if cursor.fetchone() is None:
        # The table does not exist
        return []

    # If the table exists, fetch the data
    cursor.execute("SELECT distinct settlementDate FROM short_interest")
    result = cursor.fetchall()
    return [row[0] for row in result]


def get_data_from_date_and_store(date):
    """Get data from a specific date and place it in the cache."""
    url = f"https://cdn.finra.org/equity/otcmarket/biweekly/shrt{date}.csv"
    # add a random string to user agent to avoid getting blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        + str(random.randint(0, 9))  # noqa: S311
    }
    req = requests.get(url, headers=headers, timeout=1)
    if req.status_code != 200:
        return
    data = read_csv(StringIO(req.text), delimiter="|")
    data = data.drop(
        columns=[
            "accountingYearMonthNumber",
            "issuerServicesGroupExchangeCode",
            "stockSplitFlag",
            "revisionFlag",
        ]
    )
    data.to_sql("short_interest", sqlite3.connect(DB_PATH), if_exists="append")


def prepare_data():
    """Prepare the data."""
    date_list = get_short_interest_dates()
    cached_urls = get_cached_dates()
    for date in date_list:
        if f"{date[:4]}-{date[4:6]}-{date[6:]}" not in cached_urls:
            get_data_from_date_and_store(date)
