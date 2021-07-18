""" Stockgrid View """
__docformat__ = "numpy"

import argparse
import os
from typing import List
import requests
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    export_data,
)


def darkshort(other_args: List[str]):
    """Get dark pool short positions.

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    """
    parser = argparse.ArgumentParser(
        prog="darkshort",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Get dark pool short positions. [Source: Stockgrid]",
    )
    parser.add_argument(
        "-n",
        "--number",
        help="Number of top tickers to show",
        type=check_positive,
        default=10,
        dest="num",
    )
    parser.add_argument(
        "-s",
        "--sort",
        help="Field for which to sort by, where 'sv': Short Vol. (1M), "
        "'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. (1M), "
        "'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position (1M), "
        "'dpp_dollar': DP Position ($1B)",
        choices=["sv", "sv_pct", "nsv", "nsv_dollar", "dpp", "dpp_dollar"],
        default="dpp_dollar",
        dest="sort_field",
    )
    parser.add_argument(
        "-a",
        "--ascending",
        action="store_true",
        default=False,
        dest="ascending",
        help="Data in ascending order",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        d_fields_endpoints = {
            "sv": "Short+Volume",
            "sv_pct": "Short+Volume+%25",
            "nsv": "Net+Short+Volume",
            "nsv_dollar": "Net+Short+Volume+$",
            "dpp": "Dark+Pools+Position",
            "dpp_dollar": "Dark+Pools+Position+$",
        }

        field = d_fields_endpoints[ns_parser.sort_field]

        if ns_parser.ascending:
            order = "asc"
        else:
            order = "desc"

        link = f"https://stockgridapp.herokuapp.com/get_dark_pool_data?top={field}&minmax={order}"

        response = requests.get(link)
        df = pd.DataFrame(response.json()["data"])

        df = df[
            [
                "Ticker",
                "Date",
                "Short Volume",
                "Short Volume %",
                "Net Short Volume",
                "Net Short Volume $",
                "Dark Pools Position",
                "Dark Pools Position $",
            ]
        ]
        dp_date = df["Date"].values[0]
        df = df.drop(columns=["Date"])
        df["Net Short Volume $"] = df["Net Short Volume $"] / 100_000_000
        df["Short Volume"] = df["Short Volume"] / 1_000_000
        df["Net Short Volume"] = df["Net Short Volume"] / 1_000_000
        df["Short Volume %"] = df["Short Volume %"] * 100
        df["Dark Pools Position $"] = df["Dark Pools Position $"] / (1_000_000_000)
        df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000
        df.columns = [
            "Ticker",
            "Short Vol. (1M)",
            "Short Vol. %",
            "Net Short Vol. (1M)",
            "Net Short Vol. ($100M)",
            "DP Position (1M)",
            "DP Position ($1B)",
        ]

        # Assuming that the datetime is the same, which from my experiments seems to be the case
        print(f"The following data corresponds to the date: {dp_date}")
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

        export_data(
            ns_parser.export,
            os.path.dirname(os.path.abspath(__file__)),
            "darkshort",
            df,
        )

    except Exception as e:
        print(e, "\n")


def shortvol(other_args: List[str]):
    """Print short interest and days to cover

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        prog="shortvol",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Print short interest and days to cover. [Source: Stockgrid]",
    )
    parser.add_argument(
        "-n",
        "--number",
        help="Number of top tickers to show",
        type=check_positive,
        default=10,
        dest="num",
    )
    parser.add_argument(
        "-s",
        "--sort",
        help="Field for which to sort by, where 'float': Float Short %%, "
        "'dtc': Days to Cover, 'si': Short Interest",
        choices=["float", "dtc", "si"],
        default="float",
        dest="sort_field",
    )
    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        link = "https://stockgridapp.herokuapp.com/get_short_interest?top=days"
        r = requests.get(link)
        df = pd.DataFrame(r.json()["data"])
        df.head()

        d_fields = {
            "float": "%Float Short",
            "dtc": "Days To Cover",
            "si": "Short Interest",
        }

        df = df[
            ["Ticker", "Date", "%Float Short", "Days To Cover", "Short Interest"]
        ].sort_values(
            by=d_fields[ns_parser.sort_field],
            ascending=bool(ns_parser.sort_field == "dtc"),
        )
        dp_date = df["Date"].values[0]
        df = df.drop(columns=["Date"])
        df["Short Interest"] = df["Short Interest"] / 1_000_000
        df.head()
        df.columns = [
            "Ticker",
            "Float Short %",
            "Days to Cover",
            "Short Interest (1M)",
        ]

        # Assuming that the datetime is the same, which from my experiments seems to be the case
        print(f"The following data corresponds to the date: {dp_date}")
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

        export_data(
            ns_parser.export,
            os.path.dirname(os.path.abspath(__file__)),
            "shortvol",
            df,
        )

    except Exception as e:
        print(e, "\n")
