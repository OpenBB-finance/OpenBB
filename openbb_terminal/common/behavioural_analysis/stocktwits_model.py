"""Stocktwits Model"""
__docformat__ = "numpy"

import logging
from typing import Dict, List, Tuple

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_bullbear(ticker: str) -> Tuple[int, int, int, int]:
    """Gets bullbear sentiment for ticker [Source: stocktwits]

    Parameters
    ----------
    ticker : str
        Ticker to look at

    Returns
    -------
    int
        Watchlist count
    int
        Number of cases found for ticker
    int
        Number of bullish statements
    int
        Number of bearish statements
    """
    result = requests.get(
        f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
    )
    if result.status_code == 200:
        watchlist_count = result.json()["symbol"]["watchlist_count"]
        n_cases = 0
        n_bull = 0
        n_bear = 0
        for message in result.json()["messages"]:
            if message["entities"]["sentiment"]:
                n_cases += 1
                n_bull += message["entities"]["sentiment"]["basic"] == "Bullish"
                n_bear += message["entities"]["sentiment"]["basic"] == "Bearish"

        return watchlist_count, n_cases, n_bull, n_bear
    return 0, 0, 0, 0


@log_start_end(log=logger)
def get_messages(ticker: str, limit: int = 30) -> List[str]:
    """Get last messages for a given ticker [Source: stocktwits]

    Parameters
    ----------
    ticker : str
        Stock ticker
    limit : int
        Number of messages to get

    Returns
    -------
    List[str]
        List of messages
    """
    result = requests.get(
        f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
    )
    messages = []
    if result.status_code == 200:
        for idx, message in enumerate(result.json()["messages"]):
            messages.append(message["body"])
            if idx > limit - 1:
                break
    return messages


@log_start_end(log=logger)
def get_trending() -> pd.DataFrame:
    """Get trending tickers from stocktwits [Source: stocktwits]

    Returns
    -------
    pd.DataFrame
        Dataframe of trending tickers and watchlist count
    """
    result = requests.get("https://api.stocktwits.com/api/2/trending/symbols.json")
    if result.status_code == 200:
        l_symbols = []
        for symbol in result.json()["symbols"]:
            l_symbols.append(
                [symbol["symbol"], symbol["watchlist_count"], symbol["title"]]
            )

        df_trending = pd.DataFrame(
            l_symbols, columns=["Ticker", "Watchlist Count", "Name"]
        )
        return df_trending

    return pd.DataFrame()


@log_start_end(log=logger)
def get_stalker(user: str, limit: int = 30) -> List[Dict]:
    """Gets messages from given user [Source: stocktwits]

    Parameters
    ----------
    user : str
        User to get posts for
    limit : int, optional
        Number of posts to get, by default 30
    """
    result = requests.get(f"https://api.stocktwits.com/api/2/streams/user/{user}.json")
    if result.status_code == 200:
        messages = []
        for idx, message in enumerate(result.json()["messages"]):
            messages.append(message)
            if idx > limit - 1:
                break
        return messages

    return []
