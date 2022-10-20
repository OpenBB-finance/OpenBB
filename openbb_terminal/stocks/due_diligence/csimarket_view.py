"""CSIMarket View"""
__docformat__ = "numpy"

import logging
import os

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.due_diligence import csimarket_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def suppliers(symbol: str, export: str = ""):
    """Display suppliers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    symbol: str
        Ticker to select suppliers from
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    tickers = csimarket_model.get_suppliers(symbol)
    if tickers:
        console.print(f"List of suppliers: {', '.join(tickers)}\n")
    else:
        console.print("No suppliers found.\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "supplier",
        pd.DataFrame(tickers),
    )


@log_start_end(log=logger)
def customers(symbol: str, export: str = ""):
    """Display customers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    symbol: str
        Ticker to select customers from
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    tickers = csimarket_model.get_customers(symbol)
    if tickers:
        console.print(f"List of customers: {', '.join(tickers)}\n")
    else:
        console.print("No customers found.\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "customer",
        pd.DataFrame(tickers),
    )
