"""Binance view"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

import openbb_terminal.config_terminal as cfg
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_order_book(
    from_symbol: str,
    limit: int = 100,
    to_symbol: str = "USDT",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Get order book for currency. [Source: Binance]

    Parameters
    ----------

    from_symbol: str
        Cryptocurrency symbol
    limit: int
        Limit parameter. Adjusts the weight
    to_symbol: str
        Quote currency (what to view coin vs)
    export: str
        Export dataframe data to csv,json,xlsx
    external_axes : Optional[List[plt.Axes]]
        External axes (1 axis is expected in the list), by default None
    """

    pair = from_symbol + to_symbol

    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)

    try:
        market_book = client.get_order_book(symbol=pair, limit=limit)
        bids = np.asarray(market_book["bids"], dtype=float)
        asks = np.asarray(market_book["asks"], dtype=float)
        bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
        asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
        plot_order_book(bids, asks, to_symbol, external_axes)

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "book",
            pd.DataFrame(market_book),
        )
    except BinanceAPIException:
        console.print(f"{to_symbol} is not a valid binance symbol")


@log_start_end(log=logger)
def display_balance(
    from_symbol: str, to_symbol: str = "USDT", export: str = ""
) -> None:
    """Get account holdings for asset. [Source: Binance]

    Parameters
    ----------
    from_symbol: str
        Cryptocurrency
    to_symbol: str
        Cryptocurrency
    currency: str
        Quote currency (what to view coin vs)
    export: str
        Export dataframe data to csv,json,xlsx
    """

    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)

    pair = from_symbol + to_symbol
    current_balance = client.get_asset_balance(asset=pair)
    if current_balance is None:
        console.print("Check loaded coin\n")
        return

    amounts = [float(current_balance["free"]), float(current_balance["locked"])]
    total = np.sum(amounts)
    df = pd.DataFrame(amounts).apply(lambda x: str(float(x)))
    df.columns = ["Amount"]
    df.index = ["Free", "Locked"]
    df["Percent"] = df.div(df.sum(axis=0), axis=1).round(3)
    console.print(f"\nYou currently have {total} coins and the breakdown is:")

    print_rich_table(
        df, headers=df.columns, show_index=True, title="Account Holdings for Assets"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        df,
    )
