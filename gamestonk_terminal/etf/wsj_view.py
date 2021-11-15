"""WSJ view"""
__docformat__ = "numpy"

import argparse
import os
from typing import List

from tabulate import tabulate

from gamestonk_terminal.etf import wsj_model
from gamestonk_terminal.helper_funcs import (
    export_data,
    parse_known_args_and_warn,
    try_except,
)


@try_except
def show_top_mover(sort_type: str, other_args: List[str]):
    """
    Show top ETF movers from wsj.com
    Parameters
    ----------
    sort_type: str
        What to show.  Either Gainers, Decliners or Activity
    other_args: List[str]
        Argparse arguments

    """

    parser = argparse.ArgumentParser(
        prog=sort_type,
        description="Displays top ETF/Mutual fund movers from wsj.com/market-data",
        add_help=False,
    )
    parser.add_argument("-n", help="Number to show", type=int, default=25, dest="num")

    parser.add_argument(
        "--export",
        choices=["csv", "json", "xlsx"],
        default="",
        dest="export",
        help="Export dataframe data to csv,json,xlsx file",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return
    data = wsj_model.etf_movers(sort_type)
    print(
        tabulate(
            data.iloc[: ns_parser.num],
            showindex=False,
            headers=data.columns,
            floatfmt=".2f",
            tablefmt="fancy_grid",
        )
    )
    export_data(
        ns_parser.export,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "movers"),
        sort_type,
        data,
    )
    print("")
