import logging
from datetime import datetime, timedelta

import pandas as pd
import requests

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_ipo_calendar(start_date: str = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"), end_date: str = datetime.now().strftime("%Y-%m-%d")) -> pd.DataFrame:
    """Get IPO calendar

    Parameters
    ----------
    start_date : str
        start date (%Y-%m-%d) to get IPO calendar
    end_date : str
        end date (%Y-%m-%d) to get IPO calendar

    Returns
    -------
    pd.DataFrame
        Get dataframe with economic calendar events
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/calendar/ipo?from={start_date}&to={end_date}&token={cfg.API_FINNHUB_KEY}"
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
