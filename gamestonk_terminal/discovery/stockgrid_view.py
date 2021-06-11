""" Stockgrid View """
__docformat__ = "numpy"

import argparse
from typing import List
import requests
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)


def top_dark_pools(other_args: List[str]):
    """
    Get and show the top dark pool positions
    Parameters
    ----------
    other_args: List[str[
        Argparse arguments

    """

    parser = argparse.ArgumentParser(
        prog="topdark", add_help=False, description="Get top dark pool positions"
    )
    parser.add_argument("-n", help="Number to show", type=int, default=10, dest="num")
    print("")

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        link1 = "https://stockgridapp.herokuapp.com/get_dark_pool_data?top=Dark+Pools+Position+$&minmax=desc"
        response = requests.get(link1)
        df = pd.DataFrame(response.json()["data"]).sort_values(
            "Dark Pools Position $", ascending=False
        )
        df = df[["Ticker", "Dark Pools Position $", "Dark Pools Position", "Date"]]
        df["Dark Pools Position $"] = df["Dark Pools Position $"] / (
            1_000_000_000
        )  # %%
        df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000

        df.columns = ["Ticker", "Position ($1B) ", "Shares (1M)", "Date"]
        print(
            tabulate(
                df.iloc[: ns_parser.num],
                tablefmt="fancy_grid",
                floatfmt=".2f",
                headers=list(df.columns),
                showindex=False,
            )
        )
        print("")
    except Exception as e:
        print(e, "\n")


def darkshort(other_args: List[str]):
    """
    Get short volume data from Dark Pools.
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(
        prog="darkshort", add_help=False, description="Get dark pool short positions"
    )
    parser.add_argument("-n", help="Number to show", type=int, default=10, dest="num")
    print("")

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        link = "https://stockgridapp.herokuapp.com/get_dark_pool_data?top=Dark+Pools+Position+$&minmax=desc"
        response = requests.get(link)
        df = pd.DataFrame(response.json()["data"])

        df = df[
            [
                "Ticker",
                "Date",
                "Net Short Volume",
                "Net Short Volume $",
                "Short Volume",
                "Short Volume %",
            ]
        ].sort_values(by="Net Short Volume $", ascending=False)
        df["Net Short Volume $"] = df["Net Short Volume $"] / 100_000_000
        df["Short Volume"] = df["Short Volume"] / 1_000_000
        df["Net Short Volume"] = df["Net Short Volume"] / 1_000_000
        df.columns = [
            "Ticker",
            "Date",
            "Net Short (1M)",
            "Net Short ($100M)",
            "Short Volume (1M)",
            "Short Volume %",
        ]
        print(
            tabulate(
                df.iloc[: ns_parser.num],
                tablefmt="fancy_grid",
                floatfmt=".2f",
                headers=list(df.columns),
                showindex=False,
            )
        )

        print("")
    except Exception as e:
        print(e, "\n")


def shortvol(other_args: List[str]):
    """
    Get and show short volume from stockgrid.io
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        prog="shortvol",
        add_help=False,
        description="Scrape stockgrid.io for short volume data",
    )
    parser.add_argument("-n", help="Number to show", type=int, default=10, dest="num")
    print("")

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        link = "https://stockgridapp.herokuapp.com/get_short_interest?top=days"
        r = requests.get(link)
        df = pd.DataFrame(r.json()["data"])
        df.head()

        # %%
        df = df[
            ["Ticker", "Date", "%Float Short", "Days To Cover", "Short Interest"]
        ].sort_values(by="%Float Short", ascending=False)
        df["Short Interest"] = df["Short Interest"] / 1_000_000
        df.head()
        df.columns = [
            "Ticker",
            "Date",
            "%Float Short",
            "Days To Cover",
            "Short Interest (1M)",
        ]

        print(
            tabulate(
                df.iloc[: ns_parser.num],
                tablefmt="fancy_grid",
                floatfmt=".2f",
                headers=list(df.columns),
                showindex=False,
            )
        )

    except Exception as e:
        print(e, "\n")
