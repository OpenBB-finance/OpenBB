"""SentimentInvestor Model"""
__docformat__ = "numpy"

from typing import Union, Dict, Optional
from datetime import datetime, timedelta
import logging

import pandas as pd
import requests

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end, check_api_key
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_SENTIMENTINVESTOR_TOKEN"])
def get_historical(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    number: int = 100,
) -> pd.DataFrame:
    """Get hour-level sentiment data for the chosen symbol.

    Source: [Sentiment Investor]

    Parameters
    ----------
    symbol: str
        Ticker to view sentiment data
    start_date: Optional[str]
        Initial date like string or unix timestamp (e.g. 12-21-2021)
    end_date: Optional[str]
        End date like string or unix timestamp (e.g. 12-21-2021)
    number : int
        Number of results returned by API call
        Maximum 250 per api call

    Returns
    -------
    pd.DataFrame
        Dataframe of historical sentiment
    """

    if start_date is None:
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

    if end_date is None:
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

    payload: Dict[str, Union[int, str]] = {
        "token": cfg.API_SENTIMENTINVESTOR_TOKEN,
        "symbol": symbol,
        "start": str(start_date),
        "end": str(end_date),
        "limit": number,
    }

    response = requests.get(
        "https://api.sentimentinvestor.com/v1/historical", params=payload
    )
    response_json = response.json()

    df = pd.DataFrame()

    if "results" in response_json:
        if response_json["results"]:
            df = pd.DataFrame(response_json["results"])
            df = df.set_index("timestamp_date")
            df.index = pd.to_datetime(df.index)
        else:
            console.print("No data found.\n")

    elif "error" in response_json:
        if "Authorization error" in response_json["error"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print({response_json["error"]})

    return df


@check_api_key(["API_SENTIMENTINVESTOR_TOKEN"])
def check_supported_ticker(symbol: str) -> bool:
    """Check if the ticker is supported.

    Source: [Sentiment Investor]

    Parameters
    ----------
    symbol: str
        Ticker symbol to view sentiment data

    Returns
    -------
    bool
        True if ticker is supported
    """

    payload: Dict[str, str] = {
        "token": cfg.API_SENTIMENTINVESTOR_TOKEN,
        "symbol": symbol,
    }

    response = requests.get(
        "https://api.sentimentinvestor.com/v1/supported", params=payload
    )
    if response.status_code >= 500:
        return False
    response_json = response.json()

    result = False

    if "result" in response_json:
        # if ticker is valid, payload has result key
        if response_json["result"]:
            result = response_json["result"]
        else:
            console.print(
                f"[red]Ticker {symbol} not supported. Please try another one![/red]\n"
            )

    elif "error" in response_json:
        if "Authorization error" in response_json["error"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print({response_json["error"]})

    return result


@check_api_key(["API_SENTIMENTINVESTOR_TOKEN"])
def get_trending(
    start_date: Optional[str] = None,
    hour: int = 0,
    number: int = 10,
) -> pd.DataFrame:
    """Get sentiment data on the most talked about tickers
    within the last hour Source: [Sentiment Investor].

    Parameters
    ----------
    start_date : Optional[str]
        Initial date, format YYYY-MM-DD
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

    if start_date is None:
        start_date = datetime.today().strftime("%Y-%m-%d")

    # type is datetime
    start_timestamp = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(hours=hour)

    payload: Dict[str, Union[int, str]] = {
        "token": cfg.API_SENTIMENTINVESTOR_TOKEN,
        "start": str(start_timestamp),
        "end": str(start_timestamp),
        "limit": number,
    }

    response = requests.get(
        "https://api.sentimentinvestor.com/v1/trending", params=payload
    )
    if response.status_code >= 500:
        return pd.DataFrame()

    response_json = response.json()

    df = pd.DataFrame()

    if "results" in response_json:
        if response_json["results"]:
            df = pd.DataFrame(response_json["results"])
        else:
            console.print(f"No data found for start date of {str(start_timestamp)}.\n")

    elif "error" in response_json:
        if "Authorization error" in response_json["error"]:
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print({response_json["error"]})

    return df
