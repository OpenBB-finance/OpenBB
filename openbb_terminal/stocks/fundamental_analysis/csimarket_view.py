"""CSIMarket View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import csimarket_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def suppliers(
    symbol: str, export: str = "", sheet_name: Optional[str] = None, limit: int = 10
) -> None:
    """Display suppliers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    symbol: str
        Ticker to select suppliers from
    export : str
        Export dataframe data to csv,json,xlsx file
    limit: int
        The maximum number of rows to show
    """
    tickers = csimarket_model.get_suppliers(symbol)

    if tickers.empty:
        console.print("No suppliers found.\n")
    else:
        print_rich_table(
            tickers,
            headers=list(tickers.columns),
            show_index=True,
            title=f"Suppliers for {symbol.upper()}",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "supplier",
        tickers,
        sheet_name,
    )


@log_start_end(log=logger)
def customers(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Display customers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    symbol: str
        Ticker to select customers from
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    tickers = csimarket_model.get_customers(symbol)
    if tickers.empty:
        console.print("No customers found.\n")
    else:
        # Table is a bit weird so need to change the columns header
        tickers.columns = tickers.iloc[1]
        tickers = tickers.iloc[2:]
        print_rich_table(
            tickers,
            headers=list(tickers.columns),
            show_index=True,
            title=f"Customers for {symbol.upper()}",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "customer",
        pd.DataFrame(tickers),
        sheet_name,
    )
