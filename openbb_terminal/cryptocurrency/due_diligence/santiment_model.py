import logging

import pandas as pd
import san
from san.error import SanError

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

san.ApiConfig.api_key = cfg.API_SANTIMENT_KEY


def get_slug(coin: str) -> str:
    """
    Get Santiment slug mapping and return corresponding slug for a given coin
    """
    df = san.get("projects/all")

    slug = df.loc[df["ticker"] == coin.upper()]["slug"].values[0]

    return slug


@log_start_end(log=logger)
def get_github_activity(
    coin: str, dev_activity: bool, interval: str, start: str, end: str
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
    try:
        df = san.get(
            f"{activity_type}/{slug}",
            from_date=start,
            to_date=end,
            interval=interval,
        )
    except SanError as e:
        if "Apikey" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

    return df
