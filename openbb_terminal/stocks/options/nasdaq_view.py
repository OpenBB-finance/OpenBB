"""Nasdaq View"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.stocks.options import nasdaq_model

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
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "chain_nasdaq",
        option_chain,
    )

    print_rich_table(option_chain, headers=option_chain.columns)
