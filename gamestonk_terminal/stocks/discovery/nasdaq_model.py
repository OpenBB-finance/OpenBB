"""NASDAQ DataLink Model"""
__docformat__ = "numpy"

import pandas as pd
import requests
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.helper_funcs import get_user_agent


def get_retail_tickers() -> pd.DataFrame:
    """Gets the top 10 retail stocks per day

    Returns
    -------
    pd.DataFrame
        Dataframe of tickers
    """
    r = requests.get(
        f"https://data.nasdaq.com/api/v3/datatables/NDAQ/RTAT10/?api_key={cfg.API_KEY_QUANDL}"
    )
    if r.status_code != 200:
        return pd.DataFrame()

    df = pd.DataFrame(r.json()["datatable"]["data"])
    df.columns = ["Date", "Ticker", "Activity", "Sentiment"]
    return df


def get_dividend_cal(date: str) -> pd.DataFrame:
    """Gets dividend calendar for given date.  Date represents Ex-Dividend Date

    Parameters
    ----------
    date: datetime
        Date to get for in format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame:
        Dataframe of dividend calendar
    """
    success = 69
    count = 0
    while success != 200 or count != 5:
        try:
            r = requests.get(
                f"https://api.nasdaq.com/api/calendar/dividends?date={date}",
                timeout=1,
                headers={"User-Agent": get_user_agent()},
            )
            success = r.status_code
        except requests.exceptions.ReadTimeout:
            success = 420
            count += 1

    if count == 5:
        return pd.DataFrame()
    if r.status_code == 200:
        return pd.DataFrame(r.json()["data"]["calendar"]["rows"])
    return pd.DataFrame()
