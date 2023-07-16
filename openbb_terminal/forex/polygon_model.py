"""Polygon.io model"""
__docformat__ = "numpy"

from datetime import datetime
from typing import Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key
from openbb_terminal.helper_funcs import get_user_agent, get_user_timezone, request
from openbb_terminal.rich_config import console

# pylint: disable=unsupported-assignment-operation


@check_api_key(["API_POLYGON_KEY"])
def get_historical(
    fx_pair: str,
    multiplier: int = 1,
    timespan: str = "day",
    start_date: str = "2000-01-01",
    end_date: Optional[str] = None,
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
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : Optional[str]
        Final date, format YYYY-MM-DD

    Returns
    -------
    pd.DataFrame
        Dataframe of historical forex prices
    """

    if end_date is None:
        end_date = datetime.now().date().strftime("%Y-%m-%d")

    request_url = (
        f"https://api.polygon.io/v2/aggs/ticker/C:{fx_pair}/range"
        f"/{multiplier}/{timespan}/{start_date}/{end_date}?adjusted=true&sort=desc&"
        f"limit=50000&apiKey={get_current_user().credentials.API_POLYGON_KEY}"
    )
    json_response = request(
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
    historical.index = (
        historical.index.tz_localize(tz="UTC")
        .tz_convert(get_user_timezone())
        .tz_localize(None)
    )
    return historical
