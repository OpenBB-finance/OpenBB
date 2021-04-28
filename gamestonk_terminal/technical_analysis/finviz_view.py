""" Finviz View """
__docformat__ = "numpy"

import argparse
from typing import List
from finvizfinance.quote import finvizfinance
from PIL import Image

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def view(other_args: List[str], ticker: str):
    """View historical price with trendlines. [Source: Finviz]

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker: str
        stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="view",
        description="""
            View historical price with trendlines. [Source: Finviz]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = finvizfinance(ticker)
        stock.TickerCharts()

        img = Image.open(ticker + ".jpg")
        img.show()

        print("")

    except SystemExit:
        print("")
