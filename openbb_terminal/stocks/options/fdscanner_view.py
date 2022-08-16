"""Fdscanner view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.options import fdscanner_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_options(
    limit: int = 20,
    sortby: str = "Vol/OI",
    ascending: bool = False,
    calls_only: bool = False,
    puts_only: bool = False,
    export: str = "",
):
    """Displays the unusual options table

    Parameters
    ----------
    limit: int
        Number of rows to show
    sortby: str
        Data column to sort on
    ascending: bool
        Whether to sort in ascending order
    calls_only : bool
        Flag to only show calls
    puts_only : bool
        Flag to show puts only
    export: str
        File type to export
    """
    data, last_update = fdscanner_model.unusual_options(limit)
    data = data.sort_values(by=sortby, ascending=ascending)
    if puts_only:
        data = data[data.Type == "Put"]
    if calls_only:
        data = data[data.Type == "Call"]
    print_rich_table(
        data[:limit],
        headers=list(data.columns),
        show_index=False,
        title=f"Last Updated: {last_update} (EST)",
    )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "unu_",
            data,
        )
