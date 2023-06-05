import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def get_ipo_calendar(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Get IPO calendar

    Parameters
    ----------
    start_date : Optional[str]
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Get dataframe with IPO calendar events
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    response = request(
        f"https://finnhub.io/api/v1/calendar/ipo?from={start_date}&to={end_date}&token={get_current_user().credentials.API_FINNHUB_KEY}"
    )

    df = pd.DataFrame()

    if response.status_code == 200:
        d_data = response.json()
        if "ipoCalendar" in d_data:
            d_refactor_columns = {
                "numberOfShares": "Number of Shares",
                "totalSharesValue": "Total Shares Value",
                "date": "Date",
                "exchange": "Exchange",
                "name": "Name",
                "price": "Price",
                "status": "Status",
            }
            df = pd.DataFrame(d_data["ipoCalendar"]).rename(columns=d_refactor_columns)
        else:
            console.print("Response is empty")
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df


@log_start_end(log=logger)
@check_api_key(["API_FINNHUB_KEY"])
def get_past_ipo(
    num_days_behind: int = 5,
    start_date: Optional[str] = None,
) -> pd.DataFrame:
    """Past IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_behind: int
        Number of days to look behind for IPOs dates
    start_date: str
        The starting date (format YYYY-MM-DD) to look for IPOs

    Returns
    -------
    pd.DataFrame
        Get dataframe with past IPOs
    """
    today = datetime.now()

    start = (
        (today - timedelta(days=num_days_behind)).strftime("%Y-%m-%d")
        if start_date is None
        else start_date
    )

    df_past_ipo = (
        get_ipo_calendar(start, today.strftime("%Y-%m-%d"))
        .rename(columns={"Date": "Past"})
        .fillna("")
    )

    if df_past_ipo.empty:
        console.print(f"No IPOs found since the last {num_days_behind} days")
    else:
        df_past_ipo = df_past_ipo.sort_values("Past", ascending=False)

    return df_past_ipo


@log_start_end(log=logger)
def get_future_ipo(
    num_days_ahead: int = 5,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Future IPOs dates. [Source: Finnhub]

    Parameters
    ----------
    num_days_ahead: int
        Number of days to look ahead for IPOs dates
    end_date: datetime
        The end date (format YYYY-MM-DD) to look for IPOs from today onwards

    Returns
    -------
    pd.DataFrame
        Get dataframe with future IPOs
    """
    today = datetime.now()

    end = (
        (today + timedelta(days=num_days_ahead)).strftime("%Y-%m-%d")
        if end_date is None
        else end_date
    )

    df_future_ipo = (
        get_ipo_calendar(today.strftime("%Y-%m-%d"), end)
        .rename(columns={"Date": "Future"})
        .fillna("")
    )

    if df_future_ipo.empty:
        console.print(f"No IPOs found for the next {num_days_ahead} days")
    else:
        df_future_ipo = df_future_ipo.sort_values("Future", ascending=False)

    return df_future_ipo
