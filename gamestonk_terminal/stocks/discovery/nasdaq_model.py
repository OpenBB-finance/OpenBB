"""NASDAQ DataLink Model"""
__docformat__ = "numpy"

import pandas as pd
import requests
import gamestonk_terminal.config_terminal as cfg


def get_retail_tickers() -> pd.DataFrame:
    """Gets the top 10 retail stocks per day

    Returns
    -------
    pd.DataFrame
        Dataframe of tickers
    """
    r = requests.get(
        f"https://data.nasdaq.com/api/v3/datatables/NDAQ/RTAT10/?api_key={cfg.API_KEY_QUANDL}"
    )
    if r.status_code != 200:
        return pd.DataFrame()

    df = pd.DataFrame(r.json()["datatable"]["data"])
    df.columns = ["Date", "Ticker", "Activity", "Sentiment"]
    return df
