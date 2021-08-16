"""Fdscanner view"""
__docformat__ = "numpy"

import os

import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.options import fdscanner_model


def display_options(num: int, sort_column: pd.Timestamp, export: str, ascending: bool):
    """Displays the unusual options table

    Parameters
    ----------
    num: int
        Number of rows to show
    sort_columns: pd.Timestamp
        Data column to sort on
    export: str
        File type to export
    ascending: bool
        Whether to sort in ascending order
    """
    data, last_update = fdscanner_model.unusual_options(num, sort_column, ascending)

    print(f"Last Updated: {last_update}")
    print(
        tabulate(
            data[:num], headers=data.columns, tablefmt="fancy_grid", showindex=False
        )
    )
    print("")

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "unu_",
            data,
        )
