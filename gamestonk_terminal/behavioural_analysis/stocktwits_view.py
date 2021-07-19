import argparse
from typing import List
import requests
import pandas as pd
from gamestonk_terminal.helper_funcs import check_positive, parse_known_args_and_warn


def bullbear(other_args: List[str], ticker: str):
    """
    Print bullbear sentiment based on last 30 messages on the board.
    Also prints the watchlist_count. [Source: Stocktwits]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    ticker: str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="bullbear",
        description="""
            Print bullbear sentiment based on last 30 messages on the board.
            Also prints the watchlist_count. [Source: Stocktwits]
        """,
    )
    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="ticker",
        type=str,
        default=ticker,
        help="ticker to gather sentiment from.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        result = requests.get(
            f"https://api.stocktwits.com/api/2/streams/symbol/{ns_parser.ticker}.json"
        )
        if result.status_code == 200:
            print(f"Watchlist count: {result.json()['symbol']['watchlist_count']}")
            n_cases = 0
            n_bull = 0
            n_bear = 0
            for message in result.json()["messages"]:
                if message["entities"]["sentiment"]:
                    n_cases += 1
                    n_bull += message["entities"]["sentiment"]["basic"] == "Bullish"
                    n_bear += message["entities"]["sentiment"]["basic"] == "Bearish"
            if n_cases > 0:
                print(f"\nOver {n_cases} sentiment messages:")
                print(f"Bullish {round(100*n_bull/n_cases, 2)}%")
                print(f"Bearish {round(100*n_bear/n_cases, 2)}%")
        else:
            print("Invalid symbol")
        print("")

    except Exception as e:
        print(e, "\n")


def messages(other_args: List[str], ticker: str):
    """Print up to 30 of the last messages on the board. [Source: Stocktwits]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    ticker: str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="messages",
        description="""Print up to 30 of the last messages on the board. [Source: Stocktwits]""",
    )
    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="ticker",
        type=str,
        default=ticker,
        help="get board messages from this ticker.",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_lim",
        type=check_positive,
        default=30,
        help="limit messages shown.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        result = requests.get(
            f"https://api.stocktwits.com/api/2/streams/symbol/{ns_parser.ticker}.json"
        )
        if result.status_code == 200:
            for idx, message in enumerate(result.json()["messages"]):
                print(
                    "------------------------------------------------------------------------------"
                )
                print(message["body"])
                if idx > ns_parser.n_lim - 1:
                    break
        else:
            print("Invalid symbol")
        print("")

    except Exception as e:
        print(e, "\n")


def trending(other_args: List[str]):
    """Stocks trending. [Source: Stocktwits]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="trending",
        description="""Stocks trending. [Source: Stocktwits]""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        result = requests.get("https://api.stocktwits.com/api/2/trending/symbols.json")
        if result.status_code == 200:
            l_symbols = list()
            for symbol in result.json()["symbols"]:
                l_symbols.append(
                    [symbol["symbol"], symbol["watchlist_count"], symbol["title"]]
                )

            pd.set_option("display.max_colwidth", None)
            df_trending = pd.DataFrame(
                l_symbols, columns=["Ticker", "Watchlist Count", "Name"]
            )
            print(df_trending.to_string(index=False))
        else:
            print("Error!")
        print("")

    except Exception as e:
        print(e, "\n")


def stalker(other_args: List[str]):
    """Print up to the last 30 messages of a user. [Source: Stocktwits]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="stalker",
        description="""Print up to the last 30 messages of a user. [Source: Stocktwits]""",
    )
    parser.add_argument(
        "-u",
        "--user",
        action="store",
        dest="s_user",
        type=str,
        default="Newsfilter",
        help="username.",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_lim",
        type=check_positive,
        default=30,
        help="limit messages shown.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        result = requests.get(
            f"https://api.stocktwits.com/api/2/streams/user/{ns_parser.s_user}.json"
        )

        if result.status_code == 200:
            for idx, message in enumerate(result.json()["messages"]):
                print(
                    "------------------------------------------------------------------------------"
                )
                print(message["created_at"].replace("T", " ").replace("Z", ""))
                print(message["body"])
                print("")
                if idx > ns_parser.n_lim - 1:
                    break
        else:
            print("Invalid user")
        print("")

    except Exception as e:
        print(e, "\n")
