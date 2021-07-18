""" Fidelity View """
__docformat__ = "numpy"

import argparse
from typing import List
import re
from colorama import Fore, Style
import pandas as pd

from gamestonk_terminal.helper_funcs import (
    check_positive,
    patch_pandas_text_adjustment,
    parse_known_args_and_warn,
)
from gamestonk_terminal import feature_flags as gtff

from gamestonk_terminal.discovery import fidelity_model


def buy_sell_ratio_color_red_green(val: str) -> str:
    """Add color tags to the Buys/Sells ratio cell

    Parameters
    ----------
    val : str
        Buys/Sells ratio cell

    Returns
    -------
    str
        Buys/Sells ratio cell with color tags
    """

    buy_sell_match = re.match(r"(\d+)% Buys, (\d+)% Sells", val, re.M | re.I)

    if not buy_sell_match:
        return val

    buys = int(buy_sell_match.group(1))
    sells = int(buy_sell_match.group(2))

    if buys >= sells:
        return "{}{}%{} Buys, {}% Sells".format(
            Fore.GREEN, buys, Style.RESET_ALL, sells
        )

    return f"{buys}% Buys, {Fore.RED}{sells}%{Style.RESET_ALL} Sells"


def price_change_color_red_green(val: str) -> str:
    """Add color tags to the price change cell

    Parameters
    ----------
    val : str
        Price change cell

    Returns
    -------
    str
        Price change cell with color tags
    """

    val_float = float(val.split(" ")[0])
    if val_float > 0:
        color = Fore.GREEN
    else:
        color = Fore.RED
    return color + val + Style.RESET_ALL


def orders_view(other_args: List[str]):
    """Prints a table with the last N orders by Fidelity customers

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="orders",
        description="""
            Orders by Fidelity customers. Information shown in the table below
            is based on the volume of orders entered on the "as of" date shown. Securities
            identified are not recommended or endorsed by Fidelity and are displayed for
            informational purposes only. [Source: Fidelity]
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="Number of top ordered stocks to be printed.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        order_header, df_orders = fidelity_model.get_orders()

        print(order_header, ":")

        pd.set_option("display.max_colwidth", None)

        if gtff.USE_COLOR:
            df_orders["Buy / Sell Ratio"] = df_orders["Buy / Sell Ratio"].apply(
                buy_sell_ratio_color_red_green
            )
            df_orders["Price Change"] = df_orders["Price Change"].apply(
                price_change_color_red_green
            )

            patch_pandas_text_adjustment()

        print(df_orders.head(n=ns_parser.n_num).iloc[:, :-1].to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")
