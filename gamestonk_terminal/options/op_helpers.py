"""Option helper functions"""
__docformat__ = "numpy"

import argparse
from typing import List

import pandas as pd
import numpy as np

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_non_negative,
)

# pylint: disable=R1710


def load(other_args: List[str]) -> str:
    """Load ticker into object

    Parameters
    ----------
    other_args: List[str]
        Agrparse arguments

    Returns
    -------
    str:
        Ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="opload",
        description="Load a ticker into option menu",
    )

    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="ticker",
        required="-h" not in other_args,
        help="Stock ticker",
    )

    try:
        if other_args:
            if "-t" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return ""
        print("")
        return ns_parser.ticker
    except Exception as e:
        print(e, "\n")
        return ""
    except SystemExit:
        print("")
        return ""


# pylint: disable=no-else-return


def select_option_date(avalaiable_dates: List[str], other_args: List[str]) -> str:
    """Select an option date out of a supplied list

    Parameters
    ----------
    avalaiable_dates: List[str]
        Possible date options
    other_args: List[str]
        Arparse arguments
    Returns
    -------
    expiry_date: str
        Selected expiry date
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="exp",
        description="See and set expiration date",
    )
    parser.add_argument(
        "-d",
        "--date",
        dest="n_date",
        action="store",
        type=int,
        default=-1,
        choices=range(len(avalaiable_dates)),
        help="Select index for expiry date.",
    )

    parser.add_argument(
        "-D",
        dest="date",
        type=str,
        choices=avalaiable_dates + [""],
        help="Select date (YYYY-MM-DD)",
        default="",
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-d")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return ""

        # Print possible expiry dates
        if ns_parser.n_date == -1 and not ns_parser.date:
            print("\nAvailable expiry dates:")
            for i, d in enumerate(avalaiable_dates):
                print(f"   {(2 - len(str(i))) * ' '}{i}.  {d}")
            print("")
            return ""

        # It means an expiry date was correctly selected
        else:
            if ns_parser.date:
                if ns_parser.date in avalaiable_dates:
                    print(f"Expiraration set to {ns_parser.date} \n")
                    return ns_parser.date
                else:
                    print("Expiration not an option")
                    return ""
            else:
                expiry_date = avalaiable_dates[ns_parser.n_date]
                print(f"Expiraration set to {expiry_date} \n")
                return expiry_date

    except Exception as e:
        print(e, "\n")
        return ""


def get_loss_at_strike(strike: float, chain: pd.DataFrame) -> float:
    """Function to get the loss at the given expiry

    Parameters
    ----------
    strike: Union[int,float]
        Value to calculate total loss at
    chain: Dataframe:
        Dataframe containing at least strike and openInterest

    Returns
    -------
    loss: Union[float,int]
        Total loss
    """

    itm_calls = chain[chain.index < strike][["OI_call"]]
    itm_calls["loss"] = (strike - itm_calls.index) * itm_calls["OI_call"]
    call_loss = itm_calls["loss"].sum()

    itm_puts = chain[chain.index > strike][["OI_put"]]
    itm_puts["loss"] = (itm_puts.index - strike) * itm_puts["OI_put"]
    put_loss = itm_puts.loss.sum()
    loss = call_loss + put_loss

    return loss


def calculate_max_pain(chain: pd.DataFrame) -> int:
    """Returns the max pain for a given call/put dataframe

    Parameters
    ----------
    chain: DataFrame
        Dataframe to calculate value from

    Returns
    -------
    max_pain : int
        Max pain value
    """

    strikes = np.array(chain.index)
    if ("OI_call" not in chain.columns) or ("OI_put" not in chain.columns):
        print("Incorrect columns.  Unable to parse max pain")
        return np.nan

    loss = []
    for price_at_exp in strikes:
        loss.append(get_loss_at_strike(price_at_exp, chain))

    chain["loss"] = loss
    max_pain = chain["loss"].idxmin()

    return max_pain


def vol(other_args: List[str]):
    """Parse volume argparse

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    Returns
    -------
    ns_parser: argparse.Namespace
        Parsed namespace
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="vol",
        description="Plot volume.  Volume refers to the number of contracts traded today.",
    )

    parser.add_argument(
        "-m",
        "--min",
        default=-1,
        type=check_non_negative,
        help="Min strike to plot",
        dest="min",
    )
    parser.add_argument(
        "-M",
        "--max",
        default=-1,
        type=check_non_negative,
        help="Max strike to plot",
        dest="max",
    )

    parser.add_argument(
        "--calls",
        action="store_true",
        default=False,
        dest="calls",
        help="Flag to plot call options only",
    )

    parser.add_argument(
        "--puts",
        action="store_true",
        default=False,
        dest="puts",
        help="Flag to plot put options only",
    )

    parser.add_argument(
        "--source",
        type=str,
        default="tr",
        choices=["tr", "yf"],
        dest="source",
        help="Source to get data from",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        return ns_parser

    except Exception as e:
        print(e, "\n")


def voi(other_args: List[str]):
    """Parse Volume + open interest argparse

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    Returns
    -------
    ns_parser: argparse.Namespace
        Parsed namespace
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="voi",
        description="""
                Plots Volume + Open Interest of calls vs puts.
            """,
    )
    parser.add_argument(
        "-v",
        "--minv",
        dest="min_vol",
        type=check_non_negative,
        default=-1,
        help="minimum volume (considering open interest) threshold of the plot.",
    )
    parser.add_argument(
        "-m",
        "--min",
        dest="min_sp",
        type=check_non_negative,
        default=-1,
        help="minimum strike price to consider in the plot.",
    )
    parser.add_argument(
        "-M",
        "--max",
        dest="max_sp",
        type=check_non_negative,
        default=-1,
        help="maximum strike price to consider in the plot.",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="tr",
        choices=["tr", "yf"],
        dest="source",
        help="Source to get data from",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return None
        return ns_parser

    except Exception as e:
        print(e, "\n")
        return None


def oi(other_args: List[str]):
    """Parse Open Interest argparse

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments

    Returns
    -------
    ns_parser: argparse.Namespace
        Parsed namespace
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="oi",
        description="Plot open interest.  Open interest represents the number of contracts that exist.",
    )

    parser.add_argument(
        "-m",
        "--min",
        default=-1,
        type=check_non_negative,
        help="Min strike to plot",
        dest="min",
    )
    parser.add_argument(
        "-M",
        "--max",
        default=-1,
        type=check_non_negative,
        help="Max strike to plot",
        dest="max",
    )

    parser.add_argument(
        "--calls",
        action="store_true",
        default=False,
        dest="calls",
        help="Flag to plot call options only",
    )

    parser.add_argument(
        "--puts",
        action="store_true",
        default=False,
        dest="puts",
        help="Flag to plot put options only",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="tr",
        choices=["tr", "yf"],
        dest="source",
        help="Source to get data from",
    )

    try:

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return None

        return ns_parser

    except Exception as e:
        print(e, "\n")
        return None
