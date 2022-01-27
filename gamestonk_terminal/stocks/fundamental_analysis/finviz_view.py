""" FinViz View """
__docformat__ = "numpy"

import os

from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.stocks.fundamental_analysis import finviz_model
from gamestonk_terminal.rich_config import console


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
    console.print("")
    print_rich_table(fund_data, title="Ticker Screener", show_index=True)

    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "data", fund_data)
