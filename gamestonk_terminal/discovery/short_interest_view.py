""" Short Interest View """
__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
)

from gamestonk_terminal.discovery import short_interest_model


def high_short_interest_view(other_args: List[str]):
    """Prints top N shorted stocks

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "20"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="high_short",
        description="""
            Print top stocks being more heavily shorted. HighShortInterest.com provides
            a convenient sorted database of stocks which have a short interest of over
            20 percent. Additional key data such as the float, number of outstanding shares,
            and company industry is displayed. Data is presented for the Nasdaq Stock Market,
            the New York Stock Exchange, and the American Stock Exchange. [Source: www.highshortinterest.com]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of top stocks to print.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_high_short_interest = short_interest_model.get_high_short_interest()

        pd.set_option("display.max_colwidth", None)
        print(df_high_short_interest.head(n=ns_parser.n_num).to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def low_float_view(other_args: List[str]):
    """Prints top N low float stocks

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "20"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="low_float",
        description="""
            Print top stocks with lowest float. LowFloat.com provides a convenient
            sorted database of stocks which have a float of under 10 million shares. Additional key
            data such as the number of outstanding shares, short interest, and company industry is
            displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange,
            the American Stock Exchange, and the Over the Counter Bulletin Board. [Source: www.lowfloat.com]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of top stocks to print.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_low_float = short_interest_model.get_low_float()

        pd.set_option("display.max_colwidth", None)
        print(df_low_float.head(n=ns_parser.n_num).to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")
