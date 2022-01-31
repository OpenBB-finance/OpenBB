"""Fdscanner view"""
__docformat__ = "numpy"

import logging
import os

import pandas as pd

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.options import fdscanner_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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
    print_rich_table(
        data[:num],
        headers=list(data.columns),
        show_index=False,
        title=f"Last Updated: {last_update} (EST)",
    )
    console.print("")

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "unu_",
            data,
        )
