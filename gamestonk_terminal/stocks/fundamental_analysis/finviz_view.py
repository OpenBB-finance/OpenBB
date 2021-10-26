""" FinViz View """
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.fundamental_analysis import finviz_model


def display_screen_data(ticker: str, export: str = ""):
    """FinViz ticker screener

    Parameters
    ----------
    ticker : str
        Stock ticker
    export : str
        Format to export data
    """
    fund_data = finviz_model.get_data(ticker)
    print("")
    if gtff.USE_TABULATE_DF:
        print(tabulate(fund_data, tablefmt="fancy_grid", showindex=True))
    else:
        print(fund_data.to_string(header=False))

    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "data", fund_data)
