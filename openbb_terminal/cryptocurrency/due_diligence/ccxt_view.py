"""Ccxt view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book
from openbb_terminal.cryptocurrency.due_diligence import ccxt_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_order_book(
    exchange: str,
    symbol: str,
    to_symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """Plots order book for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange : str
        exchange id
    symbol : str
        coin symbol
    vs : str
        currency to compare coin against
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    market_book = ccxt_model.get_orderbook(
        exchange=exchange, symbol=symbol, to_symbol=to_symbol
    )
    bids = np.asarray(market_book["bids"], dtype=float)
    asks = np.asarray(market_book["asks"], dtype=float)
    bids = np.insert(bids, 2, bids[:, 1].cumsum(), axis=1)
    asks = np.insert(asks, 2, np.flipud(asks[:, 1]).cumsum(), axis=1)
    fig = plot_order_book(
        bids, asks, f"{exchange.upper()}:{symbol.upper()}/{to_symbol.upper()}"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ob",
        pd.DataFrame(market_book),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_trades(
    exchange: str,
    symbol: str,
    to_symbol: str,
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Prints table showing trades for a coin in a given exchange
    [Source: https://docs.ccxt.com/en/latest/manual.html]

    Parameters
    ----------
    exchange : str
        exchange id
    symbol : str
        coin symbol
    to_symbol : str
        currency to compare coin against
    limit : int
        number of trades to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = ccxt_model.get_trades(exchange_id=exchange, symbol=symbol, to_symbol=to_symbol)
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Trades for {exchange.upper()}:{symbol.upper()}/{to_symbol.upper()}",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "trades",
        df,
        sheet_name,
    )
