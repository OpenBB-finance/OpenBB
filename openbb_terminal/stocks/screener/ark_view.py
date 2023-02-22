"""ARK View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.screener import ark_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_ark_trades(
    symbol: str,
    limit: int = 20,
    show_symbol: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display ARK trades for ticker

    Parameters
    ----------
    symbol: str
        Ticker to get trades for
    limit: int
        Number of rows to show
    show_symbol: bool
        Flag to show ticker in table
    export: str, optional
        Format to export data
    """
    ark_holdings = ark_model.get_ark_trades_by_ticker(symbol)

    if ark_holdings.empty:
        console.print(
            "Issue getting data from cathiesark.com.  Likely no trades found.\n"
        )
        return

    # Since this is for a given ticker, no need to show it
    if not show_symbol:
        ark_holdings = ark_holdings.drop(columns=["ticker"])
    ark_holdings["Total"] = ark_holdings["Total"] / 1_000_000
    ark_holdings.rename(
        columns={"Close": "Close ($)", "Total": "Total ($1M)"}, inplace=True
    )

    ark_holdings.index = pd.Series(ark_holdings.index).apply(
        lambda x: x.strftime("%Y-%m-%d")
    )
    print_rich_table(
        ark_holdings.head(limit),
        headers=list(ark_holdings.columns),
        show_index=True,
        title="ARK Trades",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "arktrades",
        ark_holdings,
        sheet_name,
    )
