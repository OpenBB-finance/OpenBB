"""SentimentInvestor Model"""
__docformat__ = "numpy"

from typing import Union, Dict
from datetime import datetime, timedelta
import logging
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
            df = pd.DataFrame(result)
            df = df.set_index("timestamp_date")
            df.index = pd.to_datetime(df.index)

            return df

    return pd.DataFrame()


def check_supported_ticker(ticker: str) -> bool:
    """Check if the ticker is supported

    Source: [Sentiment Investor]

    Parameters
    ----------
    ticker: str
        Ticker to view sentiment data

    Returns
    -------
    result: Boolean

    """

    payload: Dict[str, str] = {
        "token": cfg.API_SENTIMENTINVESTOR_TOKEN,
        "symbol": ticker,
    }

    response = requests.get(
        "https://api.sentimentinvestor.com/v1/supported", params=payload
    )

    if response.status_code == 200:

        try:
            # if ticker is valid, payload has result key
            return response.json()["result"]

        # if ticker is not valid, payload doesn't have result key
        except KeyError:
            logger.warning("KeyError: Ticker possibly not valid")

    return False


def get_trending(start: datetime, hour: int, number: int) -> pd.DataFrame:
    """Get sentiment data on the most talked about tickers
    within the last hour

    Source: [Sentiment Investor]

    Parameters
    ----------
    start: datetime
        Datetime object (e.g. datetime(2021, 12, 21)
    hour: int
        Hour of the day in 24-hour notation (e.g. 14)
    number : int
        Number of results returned by API call
        Maximum 250 per api call

    Returns
    -------
    pd.DataFrame
        Dataframe of trending data
    """

    # type is datetime
    start_timestamp = start + timedelta(hours=hour)

    payload: Dict[str, Union[int, str]] = {
        "token": cfg.API_SENTIMENTINVESTOR_TOKEN,
        "start": str(start_timestamp),
        "end": str(start_timestamp),
        "limit": number,
    }

    response = requests.get(
        "https://api.sentimentinvestor.com/v1/trending", params=payload
    )

    if response.status_code == 200:
        result = response.json()["results"]

        # check if result is not empty
        if result:
            df = pd.DataFrame(result)

            return df

    return pd.DataFrame()
