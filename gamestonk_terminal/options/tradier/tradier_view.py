"""Tradier options view"""
__docformat__ = "numpy"

import argparse
from typing import List
import os

import numpy as np
import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_non_negative,
    export_data,
)
from gamestonk_terminal.options.tradier import tradier_model

column_map = {"mid_iv": "iv", "open_interest": "oi", "volume": "vol"}


def check_valid_option_chains_headers(headers: str) -> List[str]:
    """Check valid option chains headers

    Parameters
    ----------
    headers : str
        Option chains headers

    Returns
    ----------
    List[str]
        List of columns string
    """
    columns = [str(item) for item in headers.split(",")]

    for header in columns:
        if header not in tradier_model.df_columns:
            raise argparse.ArgumentTypeError("Invalid option chains header selected!")

    return columns


def display_chains(
    chains_df: pd.DataFrame, ticker: str, expiry: str, other_args: List[str]
):
    """Display option chain

    Parameters
    ----------
    chains_df: pd.DataFrame
        Dataframe of option chain
    ticker: str
        Stock ticker
    expiry: str
        Expiration date of option
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        prog="chains",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Display option chains",
    )
    parser.add_argument(
        "--calls",
        action="store_true",
        default=False,
        dest="calls_only",
        help="Flag to show calls only",
    )
    parser.add_argument(
        "--puts",
        action="store_true",
        default=False,
        dest="puts_only",
        help="Flag to show puts only",
    )
    parser.add_argument(
        "-m",
        "--min",
        dest="min_sp",
        type=check_non_negative,
        default=-1,
        help="minimum strike price to consider.",
    )
    parser.add_argument(
        "-M",
        "--max",
        dest="max_sp",
        type=check_non_negative,
        default=-1,
        help="maximum strike price to consider.",
    )
    parser.add_argument(
        "-d",
        "--display",
        dest="to_display",
        default=tradier_model.default_columns,
        type=check_valid_option_chains_headers,
        help="columns to look at.  Columns can be:  {bid, ask, strike, bidsize, asksize, volume, open_interest, delta, "
        "gamma, theta, vega, ask_iv, bid_iv, mid_iv} ",
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

        columns = ns_parser.to_display + ["strike", "option_type"]
        chains_df = chains_df[columns].rename(columns=column_map)

        if ns_parser.min_sp == -1:
            min_strike = np.percentile(chains_df["strike"], 25)
        else:
            min_strike = ns_parser.min_sp

        if ns_parser.max_sp == -1:
            max_strike = np.percentile(chains_df["strike"], 75)
        else:
            max_strike = ns_parser.max_sp

        print(f"The strike prices are displayed between {min_strike} and {max_strike}")

        chains_df = chains_df[chains_df["strike"] >= min_strike]
        chains_df = chains_df[chains_df["strike"] <= max_strike]

        if ns_parser.export:
            # Note the extra dirname needed due to the subfolder in options
            export_data(
                ns_parser.export,
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                f"chains_{ticker}_{expiry}",
                chains_df,
            )

        calls_df = chains_df[chains_df.option_type == "call"].drop(
            columns=["option_type"]
        )
        puts_df = chains_df[chains_df.option_type == "put"].drop(
            columns=["option_type"]
        )

        if ns_parser.calls_only:
            print(
                tabulate(
                    calls_df,
                    headers=calls_df.columns,
                    tablefmt="grid",
                    showindex=False,
                    floatfmt=".2f",
                )
            )

        elif ns_parser.puts_only:
            print(
                tabulate(
                    puts_df,
                    headers=puts_df.columns,
                    tablefmt="grid",
                    showindex=False,
                    floatfmt=".2f",
                )
            )

        else:
            puts_df = puts_df[puts_df.columns[::-1]]
            chain_table = calls_df.merge(puts_df, on="strike")

            headers = [
                col.strip("_x")
                if col.endswith("_x")
                else col.strip("_y")
                if col.endswith("_y")
                else col
                for col in chain_table.columns
            ]
            print(
                tabulate(
                    chain_table,
                    headers=headers,
                    tablefmt="fancy_grid",
                    showindex=False,
                    floatfmt=".2f",
                )
            )
        print("")

    except Exception as e:
        print(e, "\n")
