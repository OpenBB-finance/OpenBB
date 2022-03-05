"""Finnhub model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_pattern_recognition(ticker: str, resolution: str) -> pd.DataFrame:
    """Get pattern recognition data

    Parameters
    ----------
    ticker : str
        Ticker to get pattern recognition data
    resolution : str
        Resolution of data to get pattern recognition from

    Returns
    -------
    pd.DataFrame
        Get datapoints corresponding to pattern signal data
    """

    response = requests.get(
        f"https://finnhub.io/api/v1/scan/pattern?symbol={ticker}&resolution={resolution}&token={cfg.API_FINNHUB_KEY}"
    )

    df = pd.DataFrame()
    # pylint:disable=no-else-return
    if response.status_code == 200:
        d_data = response.json()
        if "points" in d_data:
            df = pd.DataFrame(d_data["points"]).T
        else:
            console.print("Response is empty")
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df
