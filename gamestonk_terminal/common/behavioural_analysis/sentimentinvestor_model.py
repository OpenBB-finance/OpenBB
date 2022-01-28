"""SentimentInvestor Model"""
__docformat__ = "numpy"

import logging
from typing import Dict, Union

import pandas as pd
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_historical(ticker: str, start: str, end: str, number: int) -> pd.DataFrame:
    """Get hour-level sentiment data for the chosen ticker

    Source: [Sentiment Investor]

    Parameters
    ----------
    ticker: str
        Ticker to view sentiment data
    start: str
        Initial date like string or unix timestamp (e.g. 12-21-2021)
    end: str
        End date like string or unix timestamp (e.g. 12-21-2021)
    number : int
        Number of results returned by API call
        Maximum 250 per api call

    Returns
    -------
    pd.DataFrame
        Dataframe of historical sentiment
    """

    payload: Dict[str, Union[int, str]] = {
        "token": cfg.API_SENTIMENTINVESTOR_TOKEN,
        "symbol": ticker,
        "start": str(start),
        "end": str(end),
        "limit": number,
    }

    response = requests.get(
        "https://api.sentimentinvestor.com/v1/historical", params=payload
    )

    if response.status_code == 200:
        result = response.json()["results"]

        # check if result is not empty
        if result:
            df = pd.DataFrame(response.json()["results"])
            df = df.set_index("timestamp_date")
            df.index = pd.to_datetime(df.index)

            return df

    return pd.DataFrame()
