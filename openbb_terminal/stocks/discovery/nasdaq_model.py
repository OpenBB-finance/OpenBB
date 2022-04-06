"""NASDAQ DataLink Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

import openbb_terminal.config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.rich_config import console


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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

    df = pd.DataFrame()

    if r.status_code == 200:
        df = pd.DataFrame(r.json()["datatable"]["data"])
        df.columns = ["Date", "Ticker", "Activity", "Sentiment"]
    # Wrong API Key
    elif r.status_code == 400:
        console.print(r.text)
        console.print("\n")
    # Premium Feature
    elif r.status_code == 403:
        console.print(r.text)
        console.print("\n")
    # Catching other exception
    elif r.status_code != 200:
        console.print(r.text)
        console.print("\n")

    return df


@log_start_end(log=logger)
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
    ag = get_user_agent()
    # Nasdaq API doesn't like this user agent, thus we always get other than this particular one
    while (
        ag
        == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1"
    ):
        ag = get_user_agent()
    try:
        r = requests.get(
            f"https://api.nasdaq.com/api/calendar/dividends?date={date}",
            headers={"User-Agent": ag},
        )

        df = pd.DataFrame()

        if r.status_code == 200:
            df = pd.DataFrame(r.json()["data"]["calendar"]["rows"])

        # Wrong API Key
        elif r.status_code == 400:
            console.print(r.text)
        # Premium Feature
        elif r.status_code == 403:
            console.print(r.text)
        # Catching other exception
        elif r.status_code != 200:
            console.print(r.text)

    except requests.exceptions.ReadTimeout:
        logger.exception("Request timed out")
        return pd.DataFrame()
    return df
