"""CoinPaprika view"""
__docformat__ = "numpy"

import argparse
from typing import List
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, check_positive
import gamestonk_terminal.cryptocurrency.discovery.coinpaprika_model as paprika
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_list_of_coins,
)


def display_search_results(other_args: List[str]):
    """Search over CoinPaprika API [Source: CoinPaprika]

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="search",
        description="""Search over CoinPaprika API
        You can display only top N number of results with --top parameter.
        You can sort data by id, name , category --sort parameter and also with --descend flag to sort descending.
        To choose category in which you are searching for use --cat/-c parameter. Available categories:
        currencies|exchanges|icos|people|tags|all
        Displays:
            id, name, category""",
    )
    parser.add_argument(
        "-q",
        "--query",
        help="phrase for search",
        dest="query",
        type=str,
        required="-h" not in other_args,
    )
    parser.add_argument(
        "-c",
        "--cat",
        help="Categories to search: currencies|exchanges|icos|people|tags|all. Default: all",
        dest="category",
        default="all",
        type=str,
        choices=[
            "currencies",
            "exchanges",
            "icos",
            "people",
            "tags",
            "all",
        ],
    )
    parser.add_argument(
        "-t",
        "--top",
        default=20,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: id",
        default="id",
        choices=["category", "id", "name"],
    )
    parser.add_argument(
        "--descend",
        action="store_false",
        help="Flag to sort in descending order (lowest first)",
        dest="descend",
        default=True,
    )

    try:

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-q")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        category = ns_parser.category
        if category.lower() == "all":
            category = "currencies,exchanges,icos,people,tags"

        df = paprika.get_search_results(query=ns_parser.query, category=category)

        if df.empty:
            print(
                f"No results for search query '{ns_parser.query}' in category '{ns_parser.category}'\n"
            )
            return

        df = df.sort_values(by=ns_parser.sortby, ascending=ns_parser.descend)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    except Exception as e:
        print(e, "\n")


def display_coins(other_args: List[str]):
    """Shows list of all available coins on CoinPaprika

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="coins",
        description="""Shows list of all available coins on CoinPaprika.
        You can display top N number of coins with --top N flag,
        You can search by starting letters with -l/--letter flag like `coins -l M`
        And you can also specify by which column you are searching for coin with --key
        Displays columns like:
            rank, id, name, type""",
    )
    parser.add_argument(
        "-s",
        "--skip",
        default=0,
        dest="skip",
        help="Skip n of records",
        type=check_positive,
    )
    parser.add_argument(
        "-t",
        "--top",
        default=15,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )
    parser.add_argument("-l", "--letter", dest="letter", help="First letters", type=str)
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Search in column symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = get_list_of_coins()

        letter = ns_parser.letter
        if letter and isinstance(letter, str):
            df = df[
                df[ns_parser.key].str.match(f"^({letter.lower()}|{letter.upper()})")
            ].copy()

        try:
            df = df[ns_parser.skip : ns_parser.skip + ns_parser.top]
        except Exception as e:
            print(e)

        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    except Exception as e:
        print(e, "\n")
