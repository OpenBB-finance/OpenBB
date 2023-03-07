"""Stocktwits View"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.common.behavioural_analysis import stocktwits_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_bullbear(symbol: str):
    """
    Print bullbear sentiment based on last 30 messages on the board.
    Also prints the watchlist_count. [Source: Stocktwits]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    """
    watchlist_count, n_cases, n_bull, n_bear = stocktwits_model.get_bullbear(symbol)
    console.print(f"[yellow]Watchlist count[/yellow]: {watchlist_count}")
    if n_cases > 0:
        console.print(f"\nLast {n_cases} sentiment messages:")
        console.print(f"[green]Bullish:[/green] {round(100*n_bull/n_cases, 2)}%")
        console.print(f"[red]Bearish:[/red] {round(100*n_bear/n_cases, 2)}%")
    else:
        console.print("No messages found")


@log_start_end(log=logger)
def display_messages(symbol: str, limit: int = 30):
    """Prints up to 30 of the last messages on the board. [Source: Stocktwits].

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of messages to get
    """
    messages = stocktwits_model.get_messages(symbol, limit)

    if not messages.empty:
        print_rich_table(
            messages,
            headers=["MESSAGES"],
            show_index=False,
            title="Last Messages on Board",
        )
    else:
        console.print("No messages found in Stocktwits stream")


@log_start_end(log=logger)
def display_trending():
    """Show trensing stocks on stocktwits."""
    df_trending = stocktwits_model.get_trending()
    print_rich_table(
        df_trending,
        headers=list(df_trending.columns),
        show_index=False,
        title="Trending Stocks",
    )


@log_start_end(log=logger)
def display_stalker(user: str, limit: int = 10):
    """Show last posts for given user.

    Parameters
    ----------
    user : str
        Stocktwits username
    limit : int, optional
        Number of messages to show, by default 10
    """
    messages = stocktwits_model.get_stalker(user, limit)

    df_messages = pd.DataFrame.from_dict(messages)

    df_messages["created_at"] = pd.to_datetime(df_messages["created_at"])

    df_messages = pd.DataFrame(df_messages, columns=["created_at", "id", "body", "url"])

    # We look for a date name in the column to assume its a date on frontend side for filtering etc
    df_messages.rename(columns={"created_at": "created_at_date"}, inplace=True)

    df_messages = df_messages.drop(["id", "url"], axis=1)

    print_rich_table(
        df_messages,
        show_index=False,
        limit=limit,
    )
