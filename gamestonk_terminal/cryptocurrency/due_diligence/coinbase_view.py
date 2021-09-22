"""Coinbase view"""
__docformat__ = "numpy"

import os
from typing import Optional
import pandas as pd
from tabulate import tabulate
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.cryptocurrency.due_diligence import coinbase_model
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book

register_matplotlib_converters()


def display_order_book(product_id: str, export: str = "") -> None:
    """Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    bids, asks, pair, market_book = coinbase_model.get_order_book(product_id)
    plot_order_book(bids, asks, pair)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        pd.DataFrame(market_book),
    )


def display_trades(
    product_id: str, limit: int = 1000, side: Optional[str] = None, export: str = ""
) -> None:
    """Display last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: int
        Last <limit> of trades. Maximum is 1000.
    side: Optional[str]
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_trades(product_id, limit, side)
    df_data = df.copy()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "trades",
        df_data,
    )


def display_candles(product_id: str, interval: str, export) -> None:
    """Get candles for chosen trading pair and time interval. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1m, 5m ,15m, 1h, 6h, 24h
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_candles(product_id, interval)
    df_data = df.copy()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=True,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "candles",
        df_data,
    )


def display_stats(product_id: str, export: str) -> None:
    """Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_product_stats(product_id)
    df_data = df.copy()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stats",
        df_data,
    )
