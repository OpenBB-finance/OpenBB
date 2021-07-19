"""WSJ view """
__docformat__ = "numpy"

import argparse
from typing import List
from tabulate import tabulate

from gamestonk_terminal.economy.wsj_model import (
    market_overview,
    us_bonds,
    us_indices,
    global_bonds,
    global_currencies,
    top_commodities,
)
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def display_overview(other_args: List[str]):
    """Display market overview

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="overview",
        description="WSJ market overview",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        data = market_overview()
        print(
            tabulate(
                data,
                showindex=False,
                headers=data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def display_indices(other_args: List[str]):
    """Display us indices

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="indices",
        description="WSJ US Indices",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        data = us_indices()
        print(
            tabulate(
                data,
                showindex=False,
                headers=data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def display_futures(other_args: List[str]):
    """Display futures/commodities

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="futures",
        description="WSJ futures/commodities",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        data = top_commodities()
        print(
            tabulate(
                data,
                showindex=False,
                headers=data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def display_usbonds(other_args: List[str]):
    """Display us bonds overview

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="usbonds",
        description="WSJ US Bonds overview",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        data = us_bonds()
        print(
            tabulate(
                data,
                showindex=False,
                headers=data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def display_glbonds(other_args: List[str]):
    """Display global bond overview

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="glbond",
        description="WSJ global bond overview",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        data = global_bonds()
        print(
            tabulate(
                data,
                showindex=False,
                headers=data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def display_currencies(other_args: List[str]):
    """Display global currencies

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="currencies",
        description="WSJ currency overview",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        data = global_currencies()
        print(
            tabulate(
                data,
                showindex=False,
                headers=data.columns,
                floatfmt=".2f",
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")
