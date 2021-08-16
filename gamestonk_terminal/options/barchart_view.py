"""Helper functions for scraping options data"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.options import barchart_model


def print_options_data(ticker: str, export: str):
    """Scrapes Barchart.com for the options information

    Parameters
    ----------
    ticker: str
        Ticker to get options info for
    export: str
        Format of export file
    """

    data = barchart_model.get_options_info(ticker)

    print(tabulate(data, tablefmt="fancy_grid", showindex=False))
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "info", data)
