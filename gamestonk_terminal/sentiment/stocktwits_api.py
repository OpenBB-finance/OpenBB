import argparse
import requests
import pandas as pd
from gamestonk_terminal.helper_funcs import check_positive


# -------------------------------------------------------------------------------------------------------------------
def bullbear(l_args, s_ticker):
    parser = argparse.ArgumentParser(
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
        dest="s_ticker",
        type=str,
        default=s_ticker,
        help="ticker to gather sentiment from.",
    )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        result = requests.get(
            f"https://api.stocktwits.com/api/2/streams/symbol/{ns_parser.s_ticker}.json"
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
        print(e)
        print("")


# -------------------------------------------------------------------------------------------------------------------
def messages(l_args, s_ticker):
    parser = argparse.ArgumentParser(
        prog="messages",
        description="""Print up to 30 of the last messages on the board. [Source: Stocktwits]""",
    )

    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="s_ticker",
        type=str,
        default=s_ticker,
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
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        result = requests.get(
            f"https://api.stocktwits.com/api/2/streams/symbol/{ns_parser.s_ticker}.json"
        )
        if result.status_code == 200:
            for idx, message in enumerate(result.json()["messages"]):
                print(
                    "------------------------------------------------------------------------------------------"
                )
                print(message["body"])
                if idx > ns_parser.n_lim - 1:
                    break
        else:
            print("Invalid symbol")
        print("")

    except Exception as e:
        print(e)
        print("")


# -------------------------------------------------------------------------------------------------------------------
def trending(l_args):
    parser = argparse.ArgumentParser(
        prog="trending", description="""Stocks trending. [Source: Stocktwits]"""
    )

    try:
        (_, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        result = requests.get("https://api.stocktwits.com/api/2/trending/symbols.json")
        if result.status_code == 200:
            l_symbols = list()
            for symbol in result.json()["symbols"]:
                l_symbols.append(
                    [symbol["symbol"], symbol["watchlist_count"], symbol["title"]]
                )

            pd.set_option("display.max_colwidth", -1)
            df_trending = pd.DataFrame(
                l_symbols, columns=["Ticker", "Watchlist Count", "Name"]
            )
            print(df_trending.to_string(index=False))
        else:
            print("Error!")
        print("")

    except Exception as e:
        print(e)
        print("")


# -------------------------------------------------------------------------------------------------------------------
def stalker(l_args):
    parser = argparse.ArgumentParser(
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
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        result = requests.get(
            f"https://api.stocktwits.com/api/2/streams/user/{ns_parser.s_user}.json"
        )

        if result.status_code == 200:
            for idx, message in enumerate(result.json()["messages"]):
                print(
                    "------------------------------------------------------------------------------------------"
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
        print(e)
        print("")
