"""Helper functions for the options menu"""
__docformat__ = "numpy"

import argparse
from typing import List
import requests
import pandas as pd
import numpy as np
from tabulate import tabulate
from gamestonk_terminal.config_terminal import TRADIER_TOKEN
from gamestonk_terminal.helper_funcs import (
    check_non_negative,
    parse_known_args_and_warn,
)

option_columns = [
    "bid",
    "ask",
    "strike",
    "bidsize",
    "asksize",
    "volume",
    "open_interest",
    "option_type",
]
greek_columns = ["delta", "gamma", "theta", "vega", "ask_iv", "bid_iv", "mid_iv"]
df_columns = option_columns + greek_columns
column_map = {"mid_iv": "iv", "open_interest": "oi", "volume": "vol"}

default_columns = [
    "mid_iv",
    "vega",
    "delta",
    "gamma",
    "theta",
    "volume",
    "open_interest",
    "bid",
    "ask",
]


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
        if header not in df_columns:
            raise argparse.ArgumentTypeError("Invalid option chains header selected!")

    return columns


def process_chains(response: requests.models.Response) -> pd.DataFrame:
    """Function to take in the requests.get and return a DataFrame

    Parameters
    ----------
    response: requests.models.Response
        This is the response from tradier api.

    Returns
    -------
    opt_chain: pd.DataFrame
        Dataframe with all available options
    """
    json_response = response.json()
    options = json_response["options"]["option"]

    opt_chain = pd.DataFrame(columns=df_columns)
    for idx, option in enumerate(options):
        data = [option[col] for col in option_columns]
        data += [option["greeks"][col] for col in greek_columns]
        opt_chain.loc[idx, :] = data

    return opt_chain


def get_option_chains(symbol: str, expiry: str) -> pd.DataFrame:
    """Display option chains [Source: Tradier]"

    Parameters
    ----------
    symbol : str
        Ticker to get options for
    expiry : str
        Expiration date in the form of "YYYY-MM-DD"

    Returns
    -------
    pd.DataFrame
        Dataframe with options for the gievn Symbol and Expiration date
    """
    params = {"symbol": symbol, "expiration": expiry, "greeks": "true"}

    headers = {"Authorization": f"Bearer {TRADIER_TOKEN}", "Accept": "application/json"}

    response = requests.get(
        "https://sandbox.tradier.com/v1/markets/options/chains",
        params=params,
        headers=headers,
    )
    if response.status_code != 200:
        print("Error in request. Check TRADIER_TOKEN\n")
        return pd.DataFrame()

    chains = process_chains(response)
    return chains


def display_chains(symbol: str, expiry: str, other_args: List[str]):
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
    parser = argparse.ArgumentParser(
        prog="chains",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Display option chains [Source: Tradier]",
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
        default=default_columns,
        type=check_valid_option_chains_headers,
        help="columns to look at.  Columns can be:  {bid, ask, strike, bidsize, asksize, volume, open_interest, delta, "
        "gamma, theta, vega, ask_iv, bid_iv, mid_iv} ",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        chains_df = get_option_chains(symbol, expiry)

        if chains_df.empty:
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
