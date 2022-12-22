"""CBOE View"""
__docformat__ = "numpy"

import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import cboe_model


def display_top_of_book(symbol: str, exchange: str = "BZX"):
    """Prints Table showing top of book data [CBOE]

    Parameters
    ----------
    symbol: str
        Symbol to get data for
    exchange: str
        Exchange to get data for
    """
    bids, asks = cboe_model.get_top_of_book(symbol, exchange)

    if not bids.empty and not asks.empty:
        asks = asks[["Price", "Size"]]
        bids.columns = ["Bid " + col for col in bids.columns]
        asks.columns = ["Ask " + col for col in asks.columns]
        merged = pd.concat([bids, asks], axis=1)
        print_rich_table(
            merged,
            title=f"{symbol} Top of Book",
            show_index=False,
            headers=merged.columns,
        )

    console.print()
