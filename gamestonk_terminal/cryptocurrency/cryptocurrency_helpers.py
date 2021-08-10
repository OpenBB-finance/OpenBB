"""Cryptocurrency helpers"""
__docformat__ = "numpy"

import argparse
from typing import List, Tuple, Any, Optional, Union
import difflib
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, check_positive
from gamestonk_terminal.cryptocurrency.due_diligence import (
    pycoingecko_model,
    coinpaprika_view,
    binance_view,
)
from gamestonk_terminal.cryptocurrency.discovery.pycoingecko_model import get_coin_list
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_list_of_coins,
)


def load(
    coin: str, other_args: List[str]
) -> Tuple[Union[Optional[str], pycoingecko_model.Coin], Any]:
    """Load cryptocurrency from given source. Available sources are: CoinGecko, CoinPaprika and Binance.

    Loading coin from Binance and CoinPaprika means validation if given coins exists in chosen source,
    if yes then id of the coin is returned as a string.
    In case of CoinGecko load will return Coin object, if provided coin exists. Coin object has access to different coin
    information.

    Parameters
    ----------
    coin: str
        Coin symbol or id which is checked if exists in chosen data source.
    other_args: List[str]
        Arguments to pass to argparse

    Returns
    -------
    Tuple[Union[str, pycoingecko_model.Coin], Any]
        - str or Coin object for provided coin
        - str with source of the loaded data. CoinGecko, CoinPaprika, or Binance

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="load",
        description="Load crypto currency to perform analysis on. "
        "Available data sources are CoinGecko, CoinPaprika, and Binance"
        "By default main source used for analysis is CoinGecko (cg). To change it use --source flag",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Coin to get",
        dest="coin",
        type=str,
        required="-h" not in other_args,
    )

    parser.add_argument(
        "--source",
        dest="source",
        choices=["cp", "cg", "bin"],
        default="cg",
        help="Source of data.",
        type=str,
    )

    try:
        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return coin, None

        current_coin = ""  # type: Optional[Any]

        if ns_parser.source == "cg":
            current_coin = pycoingecko_model.Coin(ns_parser.coin)
            return current_coin, ns_parser.source

        if ns_parser.source == "bin":
            current_coin = binance_view.load(other_args)
            return current_coin, ns_parser.source

        if ns_parser.source == "cp":
            current_coin = coinpaprika_view.load(other_args)
            return current_coin, ns_parser.source

        return current_coin, None

    except KeyError:
        print(f"Could not find coin: {ns_parser.coin}", "\n")
        return coin, None
    except SystemExit:
        print("")
        return coin, None
    except Exception as e:
        print(e, "\n")
        return coin, None


def find(other_args: List[str]):
    """Find similar coin by coin name,symbol or id.

    If you don't remember exact name or id of the Coin at CoinGecko or CoinPaprika
    you can use this command to display coins with similar name, symbol or id to your search query.
    Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.
      -c, --coin stands for coin - you provide here your search query
      -k, --key it's a searching key. You can search by symbol, id or name of coin
      -t, --top it displays top N number of records.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="find",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at CoinGecko,
        or CoinPaprika you can use this command to display coins with similar name, symbol or id to your search query.
        Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
        It will search for coin that has similar name to polka and display top 25 matches.
        -c, --coin stands for coin - you provide here your search query
        -k, --key it's a searching key. You can search by symbol, id or name of coin
        -t, --top it displays top N number of records.""",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Symbol Name or Id of Coin",
        dest="coin",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Specify by which column you would like to search: symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )
    parser.add_argument(
        "-t",
        "--top",
        default=10,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )

    parser.add_argument(
        "--source",
        dest="source",
        choices=["cp", "cg"],
        default="cg",
        help="Source of data.",
        type=str,
    )

    try:

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.source == "cg":
            coins_df = get_coin_list()
            coins_list = coins_df[ns_parser.key].to_list()
            sim = difflib.get_close_matches(ns_parser.coin, coins_list, ns_parser.top)
            df = pd.Series(sim).to_frame().reset_index()
            df.columns = ["index", ns_parser.key]
            coins_df.drop("index", axis=1, inplace=True)
            df = df.merge(coins_df, on=ns_parser.key)
            print(
                tabulate(
                    df,
                    headers=df.columns,
                    floatfmt=".1f",
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )
        elif ns_parser.source == "cp":
            coins_df = get_list_of_coins()
            coins_list = coins_df[ns_parser.key].to_list()

            keys = {"name": "title", "symbol": "upper", "id": "lower"}

            key = keys.get(ns_parser.key)
            coin = getattr(ns_parser.coin, str(key))()

            sim = difflib.get_close_matches(coin, coins_list, ns_parser.top)
            df = pd.Series(sim).to_frame().reset_index()
            df.columns = ["index", ns_parser.key]
            df = df.merge(coins_df, on=ns_parser.key)
            print(
                tabulate(
                    df,
                    headers=df.columns,
                    floatfmt=".1f",
                    showindex=False,
                    tablefmt="fancy_grid",
                )
            )

        else:
            print("Couldn't execute find methods for CoinPaprika or CoinGecko")
        print("")

    except Exception as e:
        print(e, "\n")
