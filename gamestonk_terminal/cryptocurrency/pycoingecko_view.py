""" pycoingecko_api """
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from tabulate import tabulate
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI

register_matplotlib_converters()

# Generate a list of valid coins to be checked against later
cg_api = CoinGeckoAPI()
coins = cg_api.get_coins()
coin_symbol_to_id = {}
coin_ids = []

for single_coin in coins:
    coin_symbol_to_id[single_coin["symbol"]] = single_coin["id"]
    coin_ids.append(single_coin["id"])

# pylint: disable=inconsistent-return-statements
def load(other_args: List[str]):
    """Load selected Cryptocurrency

    Parameters
    ----------
    other_args : List[str]
        argparse arguments

    """
    cg = CoinGeckoAPI()
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="Crypto",
        description="""
                        Cryptocurrencies
                        """,
    )

    parser.add_argument(
        "-c",
        "--coin",
        required=True,
        type=str,
        dest="coin",
        help="Coin to load data for",
    )

    parser.add_argument(
        "-d", "--days", default=30, dest="days", help="Number of days to get data for"
    )

    parser.add_argument(
        "--vs", default="usd", dest="vs", help="Currency to display vs coin"
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        if ns_parser.coin in coin_ids:
            coin = ns_parser.coin
        else:
            try:
                coin = coin_symbol_to_id[ns_parser.coin]
            except KeyError:
                print(f"Could not find coin with the id: {ns_parser.coin}")
                print("")
                return [None, pd.DataFrame()]

        prices = cg.get_coin_market_chart_by_id(
            coin, vs_currency=ns_parser.vs, days=ns_parser.days
        )
        prices = prices["prices"]
        prices = pd.DataFrame(data=prices, columns=["Time", "Price"])
        prices["Time"] = pd.to_datetime(prices.Time, unit="ms")
        prices = prices.set_index("Time")
        prices["currency"] = ns_parser.vs
        print(f"{coin}/{ns_parser.vs} loaded")
        print("")
        return [coin, prices]

    except SystemExit:
        print("")
        return [None, pd.DataFrame()]

    except Exception as e:
        print(e)
        print("")
        return [None, pd.DataFrame()]


def view(coin: str, prices: pd.DataFrame, other_args: List[str]):
    """Plots loaded cryptocurrency

    Parameters
    ----------
    coin : str
        Cryptocurrency
    prices : pandas.DataFrame
        Dataframe containing prices and dates for selected coin
    other_args : List[str]
        argparse arguments

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="Crypto",
        description="""
                        Cryptocurrencies
                        """,
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.plot(prices.index, prices.Price, "-ok", ms=2)
        plt.xlabel("Time")
        plt.xlim(prices.index[0], prices.index[-1])
        plt.ylabel("Price")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        plt.title(f"{coin}/{prices['currency'][0]}")
        plt.show()
        print("")

    except SystemExit:
        print("")

    except Exception as e:
        print(e)
        print("")


def trend():
    """Prints top 7 coins from pycoingecko"""

    cg = CoinGeckoAPI()
    trending = cg.get_search_trending()["coins"]
    name, symbol, price, rank = [], [], [], []
    for coin in trending:
        name.append(coin["item"]["name"])
        symbol.append(coin["item"]["symbol"])
        coin_id = coin["item"]["id"]
        price.append(cg.get_price(coin_id, vs_currencies="USD")[coin_id]["usd"])
        rank.append(coin["item"]["market_cap_rank"])

    df = pd.DataFrame()
    df["name"] = name
    df["symbol"] = symbol
    df["last_price"] = price
    df["market_cap_rank"] = rank
    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        )
    )
    print("")
