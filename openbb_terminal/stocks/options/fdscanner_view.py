"""Fdscanner view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.options import fdscanner_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_options(
    limit: int = 20,
    sortby: str = "Vol/OI",
    ascend: bool = False,
    calls_only: bool = False,
    puts_only: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Displays the unusual options table

    Parameters
    ----------
    limit: int
        Number of rows to show
    sortby: str
        Data column to sort on
    ascend: bool
        Whether to sort in ascend order
    calls_only : bool
        Flag to only show calls
    puts_only : bool
        Flag to show puts only
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        File type to export
    """
    data, last_update = fdscanner_model.unusual_options(limit)
    data = data.sort_values(by=sortby, ascending=ascend)
    if puts_only:
        data = data[data.Type == "Put"]
    if calls_only:
        data = data[data.Type == "Call"]
    print_rich_table(
        data,
        headers=list(data.columns),
        show_index=False,
        title=f"Last Updated: {last_update} (EST)",
        export=bool(export),
        limit=limit,
    )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "unu_",
            data,
            sheet_name,
        )
