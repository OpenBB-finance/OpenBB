import logging

import pandas as pd
import requests

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

INTERVALS_TIMESERIES = ["5m", "15m", "30m", "1h", "1d", "1w"]


base_url = "https://data.messari.io/api/v1/"


@log_start_end(log=logger)
def get_marketcap_dominance(
    coin: str, interval: str, start: str, end: str
) -> pd.DataFrame:
    """Returns market dominance of a coin over time
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check market cap dominance
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)

    Returns
    -------
    pd.DataFrame
        market dominance percentage over time
    """

    url = base_url + f"assets/{coin}/metrics/mcap.dom/time-series"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    parameters = {
        "start": start,
        "end": end,
        "interval": interval,
    }

    r = requests.get(url, params=parameters, headers=headers)

    df = pd.DataFrame()

    if r.status_code == 200:
        df = pd.DataFrame(
            r.json()["data"]["values"], columns=["timestamp", "marketcap_dominance"]
        )

        if df.empty:
            console.print(f"No data found for {coin}.\n")
        else:
            df = df.set_index("timestamp")
            df.index = pd.to_datetime(df.index, unit="ms")

    elif r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df
