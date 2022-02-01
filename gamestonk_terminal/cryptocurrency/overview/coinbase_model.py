"""Coinbase model"""
__docformat__ = "numpy"

import logging
import pandas as pd
from gamestonk_terminal.cryptocurrency.coinbase_helpers import make_coinbase_request
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

PAIRS_FILTERS = [
    "id",
    "display_name",
    "base_currency",
    "quote_currency",
    "base_min_size",
    "base_max_size",
    "min_market_funds",
    "max_market_funds",
]


@log_start_end(log=logger)
def get_trading_pairs() -> pd.DataFrame:
    """Get a list of available currency pairs for trading. [Source: Coinbase]

    base_min_size - min order size
    base_max_size - max order size
    min_market_funds -  min funds allowed in a market order.
    max_market_funds - max funds allowed in a market order.

    Returns
    -------
    pd.DataFrame
        Available trading pairs on Coinbase
    """

    columns = [
        "id",
        "display_name",
        "base_currency",
        "quote_currency",
        "base_min_size",
        "base_max_size",
        "min_market_funds",
        "max_market_funds",
    ]
    pairs = make_coinbase_request("/products")
    return pd.DataFrame(pairs)[columns]
