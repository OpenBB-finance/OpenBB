""" pycoingecko_api """
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, plot_autoscale
from gamestonk_terminal.cryptocurrency.crypto_helper import coin_symbol_to_id, coin_ids
from gamestonk_terminal.config_plot import PLOT_DPI

register_matplotlib_converters()
# pylint: disable=inconsistent-return-statements


def load(l_args: List[str]):
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
        if l_args:
            if "-" not in l_args[0]:
                l_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, l_args)

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
                return [None, pd.DataFrame]

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


def view(coin, prices, l_args: List[str]):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

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
