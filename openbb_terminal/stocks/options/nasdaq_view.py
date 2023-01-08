"""Nasdaq View"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.helper_funcs import export_data
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.stocks.options.nasdaq_model import get_option_chain
from openbb_terminal.stocks.options.op_helpers import process_option_chain

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_chains(symbol: str, expiry: str, export: str = ""):
    """Display option chain for given expiration

    Parameters
    ----------
    symbol: str
        Ticker symbol
    expiry: str
        Expiry date for options
    export: str
        Format to export data
    """
    option_chain = get_option_chain(symbol, expiry)
    option_chain = process_option_chain(option_chain, "Nasdaq")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "chain_nasdaq",
        option_chain,
    )

    calls = option_chain[option_chain["optionType"] == "call"]
    puts = option_chain[option_chain["optionType"] == "put"]

    print_rich_table(
        calls,
        headers=list(calls.columns),
        show_index=False,
        title="Option chain - Calls",
    )
    print_rich_table(
        puts,
        headers=list(puts.columns),
        show_index=False,
        title="Option chain - Puts",
    )
