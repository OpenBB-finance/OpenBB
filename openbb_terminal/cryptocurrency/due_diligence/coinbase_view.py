"""Coinbase view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book
from openbb_terminal.cryptocurrency.due_diligence import coinbase_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_order_book(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    bids, asks, pair, market_book = coinbase_model.get_order_book(symbol)
    fig = plot_order_book(bids, asks, pair)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        pd.DataFrame(market_book),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_trades(
    symbol: str,
    limit: int = 20,
    side: Optional[str] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: int
        Last `limit` of trades. Maximum is 1000.
    side: Optional[str]
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_trades(symbol, limit, side)

    print_rich_table(
        df, headers=list(df.columns), show_index=False, export=bool(export)
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "trades",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_candles(
    symbol: str,
    interval: str = "24hour",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing candles for chosen trading pair and time interval. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour, 1day
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_candles(symbol, interval)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=True,
        title="Trading Pair Candles",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "candles",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_stats(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Prints table showing 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_product_stats(symbol)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Coinbase:{symbol.upper()} 24 hr Product Stats",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stats",
        df,
        sheet_name,
    )
