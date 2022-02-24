"""Stocktwits View"""
__docformat__ = "numpy"

import logging

import pandas as pd

from gamestonk_terminal.common.behavioural_analysis import stocktwits_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import print_rich_table
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_bullbear(ticker: str):
    """
    Print bullbear sentiment based on last 30 messages on the board.
    Also prints the watchlist_count. [Source: Stocktwits]

    Parameters
    ----------
    ticker: str
        Stock ticker
    """
    watchlist_count, n_cases, n_bull, n_bear = stocktwits_model.get_bullbear(ticker)
    console.print(f"Watchlist count: {watchlist_count}")
    if n_cases > 0:
        console.print(f"\nLast {n_cases} sentiment messages:")
        console.print(f"Bullish {round(100*n_bull/n_cases, 2)}%")
        console.print(f"Bearish {round(100*n_bear/n_cases, 2)}%")
    else:
        console.print("No messages found")
    console.print("")


@log_start_end(log=logger)
def display_messages(ticker: str, limit: int = 30):
    """Print up to 30 of the last messages on the board. [Source: Stocktwits]

    Parameters
    ----------
    ticker: str
        Stock ticker
    limit: int
        Number of messages to get
    """
    messages = stocktwits_model.get_messages(ticker, limit)

    print_rich_table(
        pd.DataFrame(messages),
        headers=["MESSAGES"],
        show_index=False,
        title="Last Messages on Board",
    )


@log_start_end(log=logger)
def display_trending():
    """Show trensing stocks on stocktwits"""
    df_trending = stocktwits_model.get_trending()
    print_rich_table(
        df_trending,
        headers=list(df_trending.columns),
        show_index=False,
        title="Trending Stocks",
    )
    console.print("")


@log_start_end(log=logger)
def display_stalker(user: str, limit: int = 10):
    """Show last posts for given user

    Parameters
    ----------
    user : str
        Stocktwits username
    limit : int, optional
        Number of messages to show, by default 10
    """
    messages = stocktwits_model.get_stalker(user, limit)
    for message in messages:
        console.print(
            "------------------------------------------------------------------------------"
        )
        console.print(message["created_at"].replace("T", " ").replace("Z", ""))
        console.print(message["body"])
        console.print("")
