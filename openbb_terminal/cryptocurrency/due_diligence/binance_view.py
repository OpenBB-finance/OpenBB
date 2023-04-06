"""Binance view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import numpy as np

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book
from openbb_terminal.cryptocurrency.due_diligence.binance_model import (
    get_balance,
    get_order_book,
)
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
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots order book for currency. [Source: Binance]

    Parameters
    ----------

    from_symbol: str
        Cryptocurrency symbol
    limit: int
        Limit parameter. Adjusts the weight
    to_symbol: str
        Quote currency (what to view coin vs)
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    market_book = get_order_book(from_symbol, limit, to_symbol)
    bids = np.asarray(market_book["bids"], dtype=float)
    asks = np.asarray(market_book["asks"], dtype=float)
    bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
    asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
    fig = plot_order_book(bids, asks, to_symbol)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        market_book,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_balance(
    from_symbol: str,
    to_symbol: str = "USDT",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints table showing account holdings for asset. [Source: Binance]

    Parameters
    ----------
    from_symbol: str
        Cryptocurrency
    to_symbol: str
        Cryptocurrency
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx
    """

    df = get_balance(from_symbol, to_symbol)

    if df is None or df.empty:
        console.print("[red]No data found[/red]\n")
        return

    total = np.sum(df["Amount"])
    console.print(f"You currently have {total} coins and the breakdown is:\n")

    print_rich_table(
        df,
        headers=df.columns,
        show_index=True,
        title="Account Holdings for Assets",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "book",
        df,
        sheet_name,
    )
