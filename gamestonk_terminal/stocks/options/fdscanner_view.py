"""Fdscanner view"""
__docformat__ = "numpy"

import os

import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.options import fdscanner_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.rich_config import console


def display_options(
    num: int,
    sort_column: pd.Timestamp,
    export: str = "",
    ascending: bool = False,
    calls_only: bool = False,
    puts_only: bool = False,
):
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
    calls_only : bool
        Flag to only show calls
    puts_only : bool
        Flag to show puts only
    """
    data, last_update = fdscanner_model.unusual_options(num)
    data = data.sort_values(by=sort_column, ascending=ascending)
    if puts_only:
        data = data[data.Type == "Put"]
    if calls_only:
        data = data[data.Type == "Call"]
    console.print(f"Last Updated: {last_update} (EST)")
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                data[:num],
                headers=data.columns,
                tablefmt="fancy_grid",
                showindex=False,
                floatfmt=["", "", ".1f", "", ".1f", ".0f", ".0f", ".2f", ".2f"],
            )
        )
    else:
        console.print(data[:num].to_string())
    console.print("")

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "unu_",
            data,
        )
