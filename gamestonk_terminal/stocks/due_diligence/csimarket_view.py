"""CSIMarket View"""
__docformat__ = "numpy"

import os
import pandas as pd
from gamestonk_terminal.stocks.due_diligence import csimarket_model
from gamestonk_terminal.helper_funcs import (
    export_data,
)
from gamestonk_terminal.rich_config import console


def suppliers(ticker: str, export: str):
    """Display suppliers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    ticker: str
        Ticker to select suppliers from
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    tickers = csimarket_model.get_suppliers(ticker)
    console.print(tickers)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "supplier",
        pd.DataFrame(tickers.split(",")),
    )


def customers(ticker: str, export: str):
    """Display customers from ticker provided. [Source: CSIMarket]

    Parameters
    ----------
    ticker: str
        Ticker to select customers from
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    tickers = csimarket_model.get_customers(ticker)
    console.print(tickers)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "customer",
        pd.DataFrame(tickers.split(",")),
    )
