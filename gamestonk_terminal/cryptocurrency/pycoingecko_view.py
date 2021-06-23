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
import gamestonk_terminal.cryptocurrency.pycoingecko_model as gecko
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


def holdings_overview(other_args: List[str]):
    """
    Shows overview of public companies that holds ethereum or bitcoin from www.coingecko.com
    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="holdings_overview",
        add_help=False,
        description="Shows overview of public companies that holds ethereum or bitcoin",
    )

    parser.add_argument(
        "-c",
        "--coin",
        dest="coin",
        type=str,
        help="companies with ethereum or bitcoin",
        default="bitcoin",
        choices=['ethereum','bitcoin'],
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_holdings_overview(endpoint=ns_parser.coin)
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

    except Exception as e:
        print(e)
        print("")


def holdings_companies_list(other_args: List[str]):
    """Shows Ethereum/Bitcoin Holdings by Public Companies from www.coingecko.com
    Track publicly traded companies around the world that are buying ethereum as part of corporate treasury

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="holdings_companies_list",
        add_help=False,
        description="Track publicly traded companies around the world that "
                    "are buying ethereum as part of corporate treasury",
    )

    parser.add_argument(
        "-c",
        "--coin",
        dest="coin",
        type=str,
        help="companies with ethereum or bitcoin",
        default="bitcoin",
        choices=['ethereum','bitcoin'],
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_companies_assets(endpoint=ns_parser.coin)
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

    except Exception as e:
        print(e)
        print("")


def gainers(other_args: List[str]):
    """Shows Largest Gainers - coins which gain the most in given period from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_gainers",
        add_help=False,
        description="Shows Largest Gainers - coins which gain the most in given period"
    )

    parser.add_argument(
        "-p",
        "--period",
        dest="period",
        type=str,
        help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
        default="1h",
        choices=['1h', '24h', '7d', '14d', '30d', '60d', '1y'],
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_gainers_or_losers(period=ns_parser.period, typ='gainers')
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

    except Exception as e:
        print(e)
        print("")


def losers(other_args: List[str]):
    """Shows Largest Losers - coins which lost the most in given period of time from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_gainers",
        add_help=False,
        description="Shows Largest Losers - coins which price dropped the most in given period"
    )

    parser.add_argument(
        "-p",
        "--period",
        dest="period",
        type=str,
        help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
        default="1h",
        choices=['1h', '24h', '7d', '14d', '30d', '60d', '1y'],
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_gainers_or_losers(period=ns_parser.period, typ='losers')
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

    except Exception as e:
        print(e)
        print("")