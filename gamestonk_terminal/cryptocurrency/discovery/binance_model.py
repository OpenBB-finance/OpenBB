"""Binance model"""
__docformat__ = "numpy"

import pandas as pd
from gamestonk_terminal.cryptocurrency.due_diligence.binance_model import (
    _get_trading_pairs,
)


def get_all_binance_trading_pairs() -> pd.DataFrame:
    """Returns all available pairs on Binance in DataFrame format.

    Returns
    -------
    pd.DataFrame
        symbol, baseAsset, quoteAsset

    """
    trading_pairs = _get_trading_pairs()
    return pd.DataFrame(trading_pairs)[["symbol", "baseAsset", "quoteAsset"]]
