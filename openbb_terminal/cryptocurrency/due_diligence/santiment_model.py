import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import read_file_data
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def get_slug(symbol: str) -> str:
    """
    Get Santiment slug mapping and return corresponding slug for a given coin
    """
    df = pd.DataFrame(read_file_data("santiment_slugs.json"))

    slug = df.loc[df["ticker"] == symbol.upper()]["slug"].values[0]

    return slug


@log_start_end(log=logger)
@check_api_key(["API_SANTIMENT_KEY"])
def get_github_activity(
    symbol: str,
    dev_activity: bool = False,
    interval: str = "1d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Returns  a list of developer activity for a given coin and time interval.

    [Source: https://santiment.net/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check github activity
    dev_activity: bool
        Whether to filter only for development activity
    interval : str
        Interval frequency (e.g., 1d)
    start_date : Optional[str]
        Initial date like string (e.g., 2021-10-01)
    end_date : Optional[str]
        End date like string (e.g., 2021-10-01)

    Returns
    -------
    pd.DataFrame
        developer activity over time
    """

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    if end_date is None:
        end_date = (datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")

    activity_type = "dev_activity" if dev_activity else "github_activity"

    slug = get_slug(symbol)

    headers = {
        "Content-Type": "application/graphql",
        "Authorization": f"Apikey {get_current_user().credentials.API_SANTIMENT_KEY}",
    }

    data = (
        f'\n{{ getMetric(metric: "{activity_type}"){{ timeseriesData( slug: "{slug}"'
        f'from: "{start_date}" to: "{end_date}" interval: "{interval}"){{ datetime value }} }} }}'
    )

    response = request(
        "https://api.santiment.net/graphql", method="POST", headers=headers, data=data
    )

    df = pd.DataFrame()

    if response.status_code == 200:
        if "getMetric" in response.json()["data"]:
            df = pd.DataFrame(response.json()["data"]["getMetric"]["timeseriesData"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.set_index("datetime")
        else:
            console.print(f"Could not find github activity found for {symbol}\n")

    elif response.status_code == 400:
        if "Apikey" in response.json()["errors"]["details"]:
            console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df
