"""NASDAQ DataLink Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_QUANDL"])
def get_retail_tickers() -> pd.DataFrame:
    """Gets the top 10 retail stocks per day

    Returns
    -------
    pd.DataFrame
        Dataframe of tickers
    """
    r = request(
        f"https://data.nasdaq.com/api/v3/datatables/NDAQ/RTAT10/?api_key={get_current_user().credentials.API_KEY_QUANDL}"
    )

    df = pd.DataFrame()

    if r.status_code == 200:
        df = pd.DataFrame(r.json()["datatable"]["data"])
        df.columns = ["Date", "Ticker", "Activity", "Sentiment"]
    else:
        console.print(r.text)

    return df


@log_start_end(log=logger)
def get_dividend_cal(date: Optional[str] = None) -> pd.DataFrame:
    """Gets dividend calendar for given date.  Date represents Ex-Dividend Date

    Parameters
    ----------
    date: datetime
        Date to get for in format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Dataframe of dividend calendar
    """
    # TODO: HELP WANTED:
    # Nasdaq API doesn't like a lot of stuff. Your ISP or VPN, the specific user agent
    # that you might be using, etc. More exploration is required to make this feature
    # equally usable for all. In the time being we patch selection of the user agent and
    # add a timeout for cases when the URL doesn't respond.

    if date is None:
        date = datetime.today().strftime("%Y-%m-%d")

    ag = get_user_agent()
    # Nasdaq API doesn't like this user agent, thus we always get other than this particular one
    while (
        ag
        == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1"
    ):
        ag = get_user_agent()
    try:
        r = request(
            f"https://api.nasdaq.com/api/calendar/dividends?date={date}",
            headers={"User-Agent": ag},
        )

        df = pd.DataFrame()

        if r.status_code == 200:
            df = pd.DataFrame(r.json()["data"]["calendar"]["rows"])

        else:
            console.print(r.text)

    except requests.exceptions.ReadTimeout:
        logger.exception("Request timed out")
        return pd.DataFrame()
    return df
