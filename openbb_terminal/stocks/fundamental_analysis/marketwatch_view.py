""" Market Watch View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import marketwatch_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def sec_filings(
    symbol: str, limit: int = 5, export: str = "", sheet_name: Optional[str] = None
):
    """Display SEC filings for a given stock ticker. [Source: Market Watch]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of ratings to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    """
    df_financials = marketwatch_model.get_sec_filings(symbol)
    print_rich_table(
        df_financials,
        headers=list(df_financials.columns),
        show_index=True,
        title="SEC Filings",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sec",
        df_financials,
        sheet_name,
    )


@log_start_end(log=logger)
def display_sean_seah_warnings(symbol: str, debug: bool = False):
    """Display Sean Seah warnings

    Parameters
    ----------
    symbol : str
        Stock ticker
    debug : bool, optional
        Whether or not to return debug messages.
        Defaults to False.
    """

    financials, warnings, debugged_warnings = marketwatch_model.get_sean_seah_warnings(
        symbol, debug
    )

    if financials.empty:
        console.print(f"No financials found for {symbol}\n")
        return

    print_rich_table(
        financials,
        headers=list(financials.columns),
        title="Sean Seah Warnings",
        show_index=True,
    )

    if not warnings:
        console.print("No warnings found. Good stonk")
        return

    messages = (
        [item for pair in zip(warnings, debugged_warnings) for item in pair]
        if debug
        else warnings
    )

    console.print("Warnings:\n")
    console.print("\n".join(messages))
