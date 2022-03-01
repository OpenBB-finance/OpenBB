"""SentimentInvestor Model"""
__docformat__ = "numpy"

from typing import Union, Dict
from datetime import datetime, timedelta
import logging

import pandas as pd
import requests

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

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

    df = pd.DataFrame()

    if "results" in response.json():
        if response.json()["results"]:
            df = pd.DataFrame(response.json()["results"])
            df = df.set_index("timestamp_date")
            df.index = pd.to_datetime(df.index)
        else:
            console.print("No data found.\n")

    elif "error" in response.json():
        if "Authorization error" in response.json()["error"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print({response.json()["error"]})

    return df


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

    result = False

    if "result" in response.json():
        # if ticker is valid, payload has result key
        if response.json()["result"]:
            result = response.json()["result"]
        else:
            console.print(
                f"[red]Ticker {ticker} not supported. Please try another one![/red]\n"
            )

    elif "error" in response.json():
        if "Authorization error" in response.json()["error"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print({response.json()["error"]})

    return result


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

    df = pd.DataFrame()

    if "results" in response.json():
        if response.json()["results"]:
            df = pd.DataFrame(response.json()["results"])
        else:
            console.print(f"No data found for start date of {str(start_timestamp)}.\n")

    elif "error" in response.json():
        if "Authorization error" in response.json()["error"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print({response.json()["error"]})

    return df
