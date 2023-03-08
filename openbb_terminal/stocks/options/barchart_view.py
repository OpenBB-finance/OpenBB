"""Helper functions for scraping options data"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.options import barchart_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def print_options_data(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Scrapes Barchart.com for the options information

    Parameters
    ----------
    symbol: str
        Ticker symbol to get options info for
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format of export file
    """

    data = barchart_model.get_options_info(symbol)

    print_rich_table(
        data,
        show_index=False,
        headers=["Info", "Value"],
        title=f"{symbol} Options Information",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "info",
        data,
        sheet_name,
    )
