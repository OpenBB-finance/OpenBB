import requests
import pandas as pd
from gamestonk_terminal import config_terminal as cfg


def get_ipo_calendar(from_date: str, to_date: str) -> pd.DataFrame:
    """Get IPO calendar

    Parameters
    ----------
    from_date : str
        from date (%Y-%m-%d) to get IPO calendar
    to_date : str
        to date (%Y-%m-%d) to get IPO calendar

    Returns
    -------
    pd.DataFrame
        Get dataframe with economic calendar events
    """
    response = requests.get(
        f"https://finnhub.io/api/v1/calendar/ipo?from={from_date}&to={to_date}&token={cfg.API_FINNHUB_KEY}"
    )
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
            return pd.DataFrame(d_data["ipoCalendar"]).rename(
                columns=d_refactor_columns
            )

    return pd.DataFrame()
