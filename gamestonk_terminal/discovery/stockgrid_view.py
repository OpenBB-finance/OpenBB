""" Stockgrid View """
__docformat__ = "numpy"

import argparse
from typing import List
import requests
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn, )

def top_dark_pools(other_args:List[str]):
    """
    Get and show the top dark pool positions
    Parameters
    ----------
    other_args: List[str[
        Argparse arguments

    """

    parser = argparse.ArgumentParser(prog="topdark",
                                     add_help=False,
                                     description="Get top dark pool positions"
                                     )
    parser.add_argument(
        "-n",
        help="Number to show",
        type = int,
        default=10,
        dest="num"
    )
    print("")

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        link1 = "https://stockgridapp.herokuapp.com/get_dark_pool_data?top=Dark+Pools+Position+$&minmax=desc"
        response = requests.get(link1)
        df = pd.DataFrame(response.json()['data']).sort_values('Dark Pools Position $', ascending=False)
        df = df[["Ticker", "Dark Pools Position $", "Dark Pools Position", "Date"]]
        df["Dark Pools Position $"] = df["Dark Pools Position $"] / (1_000_000_000)  # %%
        df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000

        df.columns = ["Ticker", "Position ($1B) ", "Shares (1M)", "Date"]
        print(
            tabulate(
                df.iloc[:ns_parser.num],
                tablefmt="fancy_grid",
                floatfmt=".2f",
                headers=list(df.columns),
                showindex=False)
        )
        print("")
    except Exception as e:
        print(e,"\n")

def darkshort(other_args:List[str]):
    """
    Get short volume data from Dark Pools.
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(prog="darkshort",
                                     add_help=False,
                                     description="Get dark pool short positions"
                                     )
    parser.add_argument(
        "-n",
        help="Number to show",
        type=int,
        default=10,
        dest="num"
    )
    print("")

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        link = "https://stockgridapp.herokuapp.com/get_dark_pool_data?top=Dark+Pools+Position+$&minmax=desc"
        response = requests.get(link1)
        df = pd.DataFrame(response.json()["data"])


        print("")
    except Exception as e:
        print(e, "\n")


def shortvol(other_args:List[str]):
    """
    Get and show short volume from stockgrid.io
    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(prog="shortvol",
                                     add_help=False,
                                     description="Scrape stockgrid.io for short volume data"
                                     )
    parser.add_argument(
        "-n",
        help="Number to show",
        type=int,
        default=10,
        dest="num"
    )
    print("")

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        link = "https://stockgridapp.herokuapp.com/get_short_interest?top=days"
        response = requests.get(link)
        df = pd.DataFrame(response.json()['data'])

    except Exception as e:
        print(e, "\n")
