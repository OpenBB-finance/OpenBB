"""Binance view"""
__docformat__ = "numpy"

import os
from binance.client import Client
from tabulate import tabulate
import numpy as np
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    export_data,
)
from gamestonk_terminal.cryptocurrency.due_diligence.binance_model import (
    plot_order_book,
)
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff


def display_order_book(coin: str, limit: int, currency: str, export: str) -> None:
    """Get order book for currency. [Source: Binance]

    Parameters
    ----------

    coin: str
        Cryptocurrency
    limit: int
        Limit parameter. Adjusts the weight
    currency: str
        Quote currency (what to view coin vs)
    export: str
        Export dataframe data to csv,json,xlsx
    """

    pair = coin + currency

    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
    market_book = client.get_order_book(symbol=pair, limit=limit)
    bids = np.asarray(market_book["bids"], dtype=float)
    asks = np.asarray(market_book["asks"], dtype=float)
    bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
    asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
    plot_order_book(bids, asks, coin)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        pd.DataFrame(market_book),
    )


def display_balance(coin: str, currency: str, export: str) -> None:
    """Get account holdings for asset. [Source: Binance]

    Parameters
    ----------
    coin: str
        Cryptocurrency
    currency: str
        Quote currency (what to view coin vs)
    export: str
        Export dataframe data to csv,json,xlsx
    """

    client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)

    pair = coin + currency
    current_balance = client.get_asset_balance(asset=pair)
    if current_balance is None:
        print("Check loaded coin")
        return

    print("")
    amounts = [float(current_balance["free"]), float(current_balance["locked"])]
    total = np.sum(amounts)
    df = pd.DataFrame(amounts).apply(lambda x: str(float(x)))
    df.columns = ["Amount"]
    df.index = ["Free", "Locked"]
    df["Percent"] = df.div(df.sum(axis=0), axis=1).round(3)
    print(f"You currently have {total} coins and the breakdown is:")

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(df, headers=df.columns, showindex=True, tablefmt="fancy_grid"),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        df,
    )
