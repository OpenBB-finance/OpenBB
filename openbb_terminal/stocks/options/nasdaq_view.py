"""Nasdaq View"""
__docformat__ = "numpy"

import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.stocks.options import nasdaq_model, op_helpers

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
    option_chain = nasdaq_model.get_option_chain(symbol, expiry)

    op_helpers.export_options(export, option_chain, "chain_nasdaq")

    print_rich_table(
        option_chain.calls,
        headers=list(option_chain.calls.columns),
        show_index=False,
        title="Option chain - Calls",
    )
    print_rich_table(
        option_chain.puts,
        headers=list(option_chain.puts.columns),
        show_index=False,
        title="Option chain - Puts",
    )
