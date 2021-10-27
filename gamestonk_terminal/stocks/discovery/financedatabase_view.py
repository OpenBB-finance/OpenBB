"""WSJ view"""
__docformat__ = "numpy"

import argparse
from typing import List

import financedatabase as fd
import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def show_equities(other_args: List[str]):
    """
    Display a selection of Equities based on country, sector, industry, name and/or description filtered
    by market cap. If no arguments are given, return the equities with the highest market cap.

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    """

    parser = argparse.ArgumentParser(
        description="Display a selection of Equities based on country, sector, industry, name and/or description "
        "filtered by market cap. If no arguments are given, return the equities with the highest "
        "market cap.",
        add_help=False,
    )

    parser.add_argument(
        "--country --c",
        default=None,
        nargs="+",
        dest="country",
        help="Specify the Equities selection based on a country",
    )

    parser.add_argument(
        "--sector --s",
        default=None,
        nargs="+",
        dest="sector",
        help="Specify the Equities selection based on a sector",
    )

    parser.add_argument(
        "--industry --i",
        default=None,
        nargs="+",
        dest="industry",
        help="Specify the Equities selection based on an industry",
    )

    parser.add_argument(
        "--name --n",
        default=None,
        nargs="+",
        dest="name",
        help="Specify the Equities selection based on the name",
    )

    parser.add_argument(
        "--description --d",
        default=None,
        nargs="+",
        dest="description",
        help="Specify the Equities selection based on the description (not shown in table)",
    )

    parser.add_argument(
        "--amount --a",
        default=10,
        type=int,
        dest="amount",
        help="Enter the number of Equities you wish to see in the Tabulate window",
    )

    parser.add_argument(
        "--options --o",
        choices=["countries", "sectors", "industries"],
        default=None,
        dest="options",
        help="Obtain the available options for country, sector and industry",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.options is not None:
            for option in fd.show_options("equities", ns_parser.options):
                print(option)
            return

        if ns_parser.country is not None:
            ns_parser.country = " ".join(ns_parser.country)
        if ns_parser.sector is not None:
            ns_parser.sector = " ".join(ns_parser.sector)
        if ns_parser.industry is not None:
            ns_parser.industry = " ".join(ns_parser.industry)

        data = fd.select_equities(
            country=ns_parser.country,
            sector=ns_parser.sector,
            industry=ns_parser.industry,
        )

        if ns_parser.name is not None:
            data = fd.search_products(
                data, query=" ".join(ns_parser.name), search="long_name"
            )
        if ns_parser.description is not None:
            data = fd.search_products(
                data, query=" ".join(ns_parser.description), search="summary"
            )

        tabulate_data = pd.DataFrame(data).T[
            [
                "long_name",
                "sector",
                "industry",
                "country",
                "city",
                "website",
                "market_cap",
            ]
        ]
        tabulate_data_sorted = tabulate_data.sort_values(
            by="market_cap", ascending=False
        )

        print(
            tabulate(
                tabulate_data_sorted.iloc[: ns_parser.amount],
                showindex=True,
                headers=[
                    "Name",
                    "Sector",
                    "Industry",
                    "Country",
                    "City",
                    "Website",
                    "Market Cap",
                ],
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )

    except KeyError:
        print("No Equities found for the used selection. \n")
    except Exception as e:
        print(e, "\n")
