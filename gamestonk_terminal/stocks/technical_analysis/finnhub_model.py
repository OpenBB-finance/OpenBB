"""Finnhub model"""
__docformat__ = "numpy"

import requests
import pandas as pd

from gamestonk_terminal import config_terminal as cfg


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

    # pylint:disable=no-else-return
    if response.status_code == 200:
        d_data = response.json()
        if "points" in d_data:
            return pd.DataFrame(d_data["points"]).T
        else:
            print("Response is empty")
            return pd.DataFrame()
    else:
        print(f"Error in requests with code: {response.status_code}")
        return pd.DataFrame()
