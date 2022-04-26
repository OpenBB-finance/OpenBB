import logging

import requests

import pandas as pd

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import read_file_data

logger = logging.getLogger(__name__)


def get_slug(coin: str) -> str:
    """
    Get Santiment slug mapping and return corresponding slug for a given coin
    """
    df = pd.DataFrame(read_file_data("santiment_slugs.json"))

    slug = df.loc[df["ticker"] == coin.upper()]["slug"].values[0]

    return slug


@log_start_end(log=logger)
def get_github_activity(
    coin: str,
    dev_activity: bool,
    interval: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    """Returns  a list of developer activity for a given coin and time interval.

    [Source: https://santiment.net/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check github activity
    dev_activity: bool
        Whether to filter only for development activity
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)

    Returns
    -------
    pd.DataFrame
        developer activity over time
    """

    activity_type = "dev_activity" if dev_activity else "github_activity"

    slug = get_slug(coin)

    headers = {
        "Content-Type": "application/graphql",
        "Authorization": f"Apikey {cfg.API_SANTIMENT_KEY}",
    }

    # pylint: disable=line-too-long
    data = f'\n{{ getMetric(metric: "{activity_type}"){{ timeseriesData( slug: "{slug}" from: "{start}" to: "{end}" interval: "{interval}"){{ datetime value }} }} }}'  # noqa: E501

    response = requests.post(
        "https://api.santiment.net/graphql", headers=headers, data=data
    )

    df = pd.DataFrame()

    if response.status_code == 200:

        if "getMetric" in response.json()["data"]:
            df = pd.DataFrame(response.json()["data"]["getMetric"]["timeseriesData"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.set_index("datetime")
        else:
            console.print(f"Could not find github activity found for {coin}\n")

    elif response.status_code == 400:
        if "Apikey" in response.json()["errors"]["details"]:
            console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df
