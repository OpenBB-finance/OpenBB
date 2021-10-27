"""WSJ view"""
__docformat__ = "numpy"

import argparse
from typing import List

import financedatabase as fd
import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def show_etfs(other_args: List[str]):
    """
    Display a selection of ETFs based on category, name and/or description filtered by total assets.
    Returns the top ETFs when no argument is given.

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    """

    parser = argparse.ArgumentParser(
        description="Display a selection of ETFs based on category, name and/or description filtered by total assets. "
        "Returns the top ETFs when no argument is given.",
        add_help=False,
    )

    parser.add_argument(
        "--category --c",
        default=None,
        nargs="+",
        dest="category",
        help="Specify the ETF selection based on a category",
    )

    parser.add_argument(
        "--name --n",
        default=None,
        nargs="+",
        dest="name",
        help="Specify the ETF selection based on the name",
    )

    parser.add_argument(
        "--description --d",
        default=None,
        nargs="+",
        dest="description",
        help="Specify the ETF selection based on the description (not shown in table)",
    )

    parser.add_argument(
        "--amount --a",
        default=10,
        type=int,
        dest="amount",
        help="Enter the number of ETFs you wish to see in the Tabulate window",
    )

    parser.add_argument(
        "--options",
        "--o",
        action="store_true",
        help="Obtain the available categories",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.options:
            for option in fd.show_options("etfs"):
                print(option)
            return

        if ns_parser.category is not None:
            data = fd.select_etfs(category=" ".join(ns_parser.category))
        else:
            data = fd.select_etfs(category=ns_parser.category)

        if ns_parser.name is not None:
            data = fd.search_products(
                data, query=" ".join(ns_parser.name), search="long_name"
            )
        if ns_parser.description is not None:
            data = fd.search_products(
                data, query=" ".join(ns_parser.description), search="summary"
            )

        tabulate_data = pd.DataFrame(data).T[
            ["long_name", "family", "category", "total_assets"]
        ]
        tabulate_data_sorted = tabulate_data.sort_values(
            by="total_assets", ascending=False
        )

        print(
            tabulate(
                tabulate_data_sorted.iloc[: ns_parser.amount],
                showindex=True,
                headers=["Name", "Family", "Category", "Total Assets"],
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )

    except KeyError:
        print("No ETFs found for the used selection. \n")
    except Exception as e:
        print(e, "\n")
