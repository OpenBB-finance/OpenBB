"""Polygon.io model"""
__docformat__ = "numpy"

from datetime import datetime
import requests
import pandas as pd
from openbb_terminal.config_terminal import API_POLYGON_KEY as api_key
from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.rich_config import console


def get_historical(
    fx_pair: str,
    multiplier: int = 1,
    timespan: str = "day",
    from_date: str = "2000-01-01",
    to_date: str = datetime.now().date().strftime("%Y-%m-%d"),
) -> pd.DataFrame:
    """Load historical fx data from polygon

    Parameters
    ----------
    fx_pair: str
        Forex pair to download
    multiplier: int
        Multiplier for timespan.  5 with minute timespan indicated 5min windows
    timespan: str
        Window to aggregate data.
    from_date: str
        Start time of data
    to_date: str
        End date of data

    Returns
    -------
    pd.DataFrame
        Dataframe of historical forex prices
    """
    request_url = (
        f"https://api.polygon.io/v2/aggs/ticker/C:{fx_pair}/range"
        f"/{multiplier}/{timespan}/{from_date}/{to_date}?adjusted=true&sort=desc&limit=50000&apiKey={api_key}"
    )
    json_response = requests.get(
        request_url, headers={"User-Agent": get_user_agent()}
    ).json()

    if json_response["status"] == "ERROR":
        console.print(f"[red]{json_response['error']}[/red]\n")
        return pd.DataFrame()

    if "results" not in json_response.keys():
        console.print("[red]Error in polygon request[/red]\n")
        return pd.DataFrame()

    historical = pd.DataFrame(json_response["results"]).rename(
        columns={
            "o": "Open",
            "c": "Close",
            "h": "High",
            "l": "Low",
            "t": "date",
            "v": "Volume",
            "n": "Transactions",
        }
    )
    historical["date"] = pd.to_datetime(historical.date, unit="ms")
    historical = historical.sort_values(by="date", ascending=True)
    historical = historical.set_index("date")
    return historical
