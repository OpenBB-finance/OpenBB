""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
import webbrowser
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def map_sp500_view(other_args: List[str]):
    """Opens Finviz website in a browser

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-p", "6m", "-t", "sp500"]
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="map",
        description="""
            Performance index stocks map categorized by sectors and industries.
            Size represents market cap. Opens web-browser. [Source: Finviz]
        """,
    )

    parser.add_argument(
        "-p",
        "--period",
        action="store",
        dest="s_period",
        type=str,
        default="1d",
        choices=["1d", "1w", "1m", "3m", "6m", "1y"],
        help="Performance period.",
    )
    parser.add_argument(
        "-t",
        "--type",
        action="store",
        dest="s_type",
        type=str,
        default="sp500",
        choices=["sp500", "world", "full", "etf"],
        help="Map filter type.",
    )

    # Conversion from period and type, to fit url requirements
    d_period = {"1d": "", "1w": "w1", "1m": "w4", "3m": "w13", "6m": "w26", "1y": "w52"}
    d_type = {"sp500": "sec", "world": "geo", "full": "sec_all", "etf": "etf"}

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    webbrowser.open(
        f"https://finviz.com/map.ashx?t={d_type[ns_parser.s_type]}&st={d_period[ns_parser.s_period]}"
    )
    print("")
