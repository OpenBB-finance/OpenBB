"""Option helper functions"""
__docformat__ = "numpy"

import argparse
from typing import List

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

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

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-d")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return ""

        # Print possible expiry dates
        if ns_parser.n_date == -1:
            print("\nAvailable expiry dates:")
            for i, d in enumerate(avalaiable_dates):
                print(f"   {(2 - len(str(i))) * ' '}{i}.  {d}")
            print("")
            return ""

        # It means an expiry date was correctly selected
        else:
            expiry_date = avalaiable_dates[ns_parser.n_date]
            return expiry_date

    except Exception as e:
        print(e, "\n")
        return ""
