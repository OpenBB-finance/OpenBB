""" ARK View """
__docformat__ = "numpy"

import argparse
from typing import List
from colorama import Fore, Style
import pandas as pd

from gamestonk_terminal.helper_funcs import (
    check_positive,
    patch_pandas_text_adjustment,
    parse_known_args_and_warn,
)
from gamestonk_terminal import feature_flags as gtff

from gamestonk_terminal.discovery import ark_model


def direction_color_red_green(val: str) -> str:
    """Adds color tags to the Direction information: Buy -> Green, Sell -> Red

    Parameters
    ----------
    val : str
        Direction string - either Buy or Sell

    Returns
    -------
    str
        Direction string with color tags added
    """

    if val == "Buy":
        ret = Fore.GREEN + val + Style.RESET_ALL
    elif val == "Sell":
        ret = Fore.RED + val + Style.RESET_ALL
    else:
        ret = val

    return ret


def ark_orders_view(other_args: List[str]):
    """Prints a table of the last N ARK Orders

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ARK Orders",
        description="""
            Orders by ARK Investment Management LLC - https://ark-funds.com/. [Source: https://cathiesark.com]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=20,
        help="Last N orders.",
    )

    try:

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_orders = ark_model.get_ark_orders()

        if df_orders.empty:
            print("The ARK orders aren't anavilable at the moment.\n")
            return

        pd.set_option("mode.chained_assignment", None)
        df_orders = ark_model.add_order_total(df_orders.head(ns_parser.n_num))

        if gtff.USE_COLOR:
            df_orders["direction"] = df_orders["direction"].apply(
                direction_color_red_green
            )

            patch_pandas_text_adjustment()

        df_orders["link"] = "https://finviz.com/quote.ashx?t=" + df_orders["ticker"]

        pd.set_option("display.max_colwidth", None)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.float_format", "{:,.2f}".format)
        print("")
        print("Orders by ARK Investment Management LLC")
        print("")
        print(df_orders.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")
