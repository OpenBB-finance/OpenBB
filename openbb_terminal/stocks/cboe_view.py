"""CBOE View"""
__docformat__ = "numpy"

from openbb_terminal.stocks import cboe_model
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console


def display_top_of_book(symbol: str, exchange: str = "BZX"):
    """Display top of book data [CBOE]

    Parameters
    ----------
    symbol: str
        Symbol to get data for
    exchange: str
        Exchange to get data for
    """
    bids, asks = cboe_model.get_top_of_book(symbol, exchange)

    if not bids.empty and not asks.empty:
        print_rich_table(
            bids, title=f"{symbol} Bids", show_index=False, headers=bids.columns
        )
        print_rich_table(
            asks, title=f"{symbol} Asks", show_index=False, headers=asks.columns
        )
    console.print()
