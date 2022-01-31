"""NASDAQ DataLink Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

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
    if r.status_code != 200:
        return pd.DataFrame()

    df = pd.DataFrame(r.json()["datatable"]["data"])
    df.columns = ["Date", "Ticker", "Activity", "Sentiment"]
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
        if r.status_code == 200:
            return pd.DataFrame(r.json()["data"]["calendar"]["rows"])
    except requests.exceptions.ReadTimeout:
        return pd.DataFrame()
    return pd.DataFrame()
