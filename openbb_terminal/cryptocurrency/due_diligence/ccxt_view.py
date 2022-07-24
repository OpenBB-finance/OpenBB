"""Ccxt view"""
__docformat__ = "numpy"

import os
from typing import List, Optional

from matplotlib import pyplot as plt
import numpy as np
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book
from openbb_terminal.cryptocurrency.due_diligence import ccxt_model
from openbb_terminal.helper_funcs import export_data, print_rich_table


def display_order_book(
    exchange: str,
    coin: str,
    vs: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
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
    df = ccxt_model.get_trades(exchange_id=exchange, coin=coin, vs=vs)
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
