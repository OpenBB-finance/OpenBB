"""Coinbase view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt

from openbb_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book
from openbb_terminal.cryptocurrency.due_diligence import coinbase_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_order_book(
    product_id: str,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    bids, asks, pair, market_book = coinbase_model.get_order_book(product_id)
    plot_order_book(bids, asks, pair, external_axes)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        pd.DataFrame(market_book),
    )


@log_start_end(log=logger)
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

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "trades",
        df_data,
    )


@log_start_end(log=logger)
def display_candles(product_id: str, interval: str = "24h", export: str = "") -> None:
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

    print_rich_table(
        df, headers=list(df.columns), show_index=True, title="Trading Pair Candles"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "candles",
        df_data,
    )


@log_start_end(log=logger)
def display_stats(product_id: str, export: str = "") -> None:
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

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="24 hr Product Stats"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stats",
        df_data,
    )
