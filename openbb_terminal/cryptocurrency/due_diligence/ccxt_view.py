"""Ccxt view"""
__docformat__ = "numpy"

import os
from typing import List, Optional

from matplotlib import pyplot as plt
import numpy as np
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book
from openbb_terminal.cryptocurrency.dataframe_helpers import prettify_column_names
from openbb_terminal.cryptocurrency.due_diligence import ccxt_model
from openbb_terminal.helper_funcs import export_data, print_rich_table


def display_order_book(
    exchange: str,
    coin: str,
    vs: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Displays order book for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange : str
        exchange id
    coin : str
        coin symbol
    vs : str
        currency to compare coin against
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    market_book = ccxt_model.get_orderbook(exchange_id=exchange, coin=coin, vs=vs)
    bids = np.asarray(market_book["bids"], dtype=float)
    asks = np.asarray(market_book["asks"], dtype=float)
    bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
    asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
    plot_order_book(
        bids, asks, f"{exchange.upper()}:{coin.upper()}/{vs.upper()}", external_axes
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ob",
        market_book,
    )


def display_trades(exchange: str, coin: str, vs: str, top: int = 10, export: str = ""):
    """Displays trades for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange : str
        exchange id
    coin : str
        coin symbol
    vs : str
        currency to compare coin against
    top : int
        number of trades to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = ccxt_model.get_trades(exchange_id=exchange, coin=coin, vs=vs)
    df.rename(columns={"datetime": "date"}, inplace=True)

    df.columns = prettify_column_names(df.columns)
    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title=f"Trades for {exchange.upper()}:{coin.upper()}/{vs.upper()}",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "trades",
        df,
    )
