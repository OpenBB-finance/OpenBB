"""Geek of wall street view"""
__docformat__ = "numpy"
import os

import pandas as pd

from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.stocks.discovery import geekofwallstreet_model as gwt_model

# pylint:disable=no-member


def display_realtime_earnings(export: str = ""):
    """Displays real time earnings data from geekofwallstreet.com

    Parameters
    ----------
    export : str, optional
        Format to export data
    """
    earnings: pd.DataFrame = gwt_model.get_realtime_earnings()
    earnings_export = earnings.copy()
    # Make the table look pretty
    earnings = earnings.drop(
        columns=[
            "Name",
            "Previous Earnings Date",
            "Stock Type",
            "Confirmation",
            "Special Case",
            "Conference Call",
            "Press Release",
            "Has Options",
        ]
    ).fillna("")
    earnings["Market Cap"] = earnings["Market Cap"] / 1_000_000_000
    earnings = earnings.rename(columns={"Market Cap": "Market Cap ($1B)"})
    print_rich_table(
        earnings,
        headers=list(earnings.columns),
        show_index=False,
        title="Real Time Earnings",
    )

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "rtearn", earnings_export
    )
