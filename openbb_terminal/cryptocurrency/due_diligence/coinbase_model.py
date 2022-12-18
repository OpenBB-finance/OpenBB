"""Coinbase model"""
__docformat__ = "numpy"

import logging
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd

from openbb_terminal.cryptocurrency.coinbase_helpers import (
    check_validity_of_product,
    make_coinbase_request,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_available_pairs_for_given_symbol(symbol: str = "ETH") -> Tuple[str, list]:
    """Return all available quoted assets for given symbol. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Uppercase symbol of coin e.g BTC, ETH, UNI, LUNA, DOT ...

    Returns
    -------
    Tuple[str, list]
        Symbol and list of available pairs
    """
    pairs = make_coinbase_request("/products")
    df = pd.DataFrame(pairs)[["base_currency", "quote_currency"]]

    if not isinstance(symbol, str):
        console.print(
            f"You did not provide correct symbol {symbol}. Symbol needs to be a string.\n"
        )
        return symbol, []

    coin_df = df[df["base_currency"] == symbol.upper()]
    return symbol, coin_df["quote_currency"].to_list()


@log_start_end(log=logger)
def get_trading_pair_info(symbol: str) -> pd.DataFrame:
    """Get information about chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    pd.DataFrame
        Basic information about given trading pair
    """

    product_id = check_validity_of_product(symbol)
    pair = make_coinbase_request(f"/products/{product_id}")
    df = pd.Series(pair).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    console.print(df)
    return df


@log_start_end(log=logger)
def get_order_book(symbol: str) -> Tuple[np.ndarray, np.ndarray, str, dict]:
    """Get orders book for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    Tuple[np.array, np.array, str, dict]
        array with bid prices, order sizes and cumulative order sizes
        array with ask prices, order sizes and cumulative order sizes
        trading pair
        dict with raw data
    """

    # TODO: Order price > current price. E.g current price 200 USD, sell order with 10000 USD
    #  makes chart look very ugly (bad scaling). Think about removing outliers or add log scale ?

    product_id = check_validity_of_product(symbol)
    market_book = make_coinbase_request(f"/products/{product_id}/book?level=2")

    size = min(
        len(market_book["bids"]), len(market_book["asks"])
    )  # arrays needs to have equal size.

    market_book["bids"] = market_book["bids"][:size]
    market_book["asks"] = market_book["asks"][:size]
    market_book.pop("sequence")

    bids = np.asarray(market_book["bids"], dtype=float)[:size]
    asks = np.asarray(market_book["asks"], dtype=float)[:size]

    bids = np.insert(bids, 3, (bids[:, 1] * bids[:, 2]).cumsum(), axis=1)
    asks = np.insert(asks, 3, np.flipud(asks[:, 1] * asks[:, 2]).cumsum(), axis=1)
    bids = np.delete(bids, 2, axis=1)
    asks = np.delete(asks, 2, axis=1)
    return bids, asks, product_id, market_book


@log_start_end(log=logger)
def get_trades(
    symbol: str, limit: int = 1000, side: Optional[Any] = None
) -> pd.DataFrame:
    """Get last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: int
        Last `limit` of trades. Maximum is 1000.
    side: str
        You can chose either sell or buy side. If side is not set then all trades will be displayed.

    Returns
    -------
    pd.DataFrame
        Last N trades for chosen trading pairs.
    """

    params = {"limit": limit}
    if side is not None and side in ["buy", "sell"]:
        params["side"] = side

    product_id = check_validity_of_product(symbol)
    product = make_coinbase_request(f"/products/{product_id}/trades", params=params)
    return pd.DataFrame(product)[["time", "price", "size", "side"]]


@log_start_end(log=logger)
def get_candles(symbol: str, interval: str = "24hour") -> pd.DataFrame:
    """Get candles for chosen trading pair and time interval. [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour, 1day

    Returns
    -------
    pd.DataFrame
        Candles for chosen trading pair.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.crypto.dd.candle(symbol="eth-usdt", interval="24hour")
    """

    interval_map = {
        "1min": 60,
        "5min": 300,
        "15min": 900,
        "1hour": 3600,
        "6hour": 21600,
        "24hour": 86400,
        "1day": 86400,
    }
    if interval not in interval_map:
        console.print(
            f"Wrong interval. Please use on from {list(interval_map.keys())}\n"
        )
        return pd.DataFrame()

    granularity: int = interval_map[interval]

    product_id = check_validity_of_product(symbol)
    candles = make_coinbase_request(
        f"/products/{product_id}/candles", params={"granularity": granularity}
    )
    df = pd.DataFrame(candles)
    df.columns = [
        "date",
        "Low",
        "High",
        "Open",
        "Close",
        "Volume",
    ]
    return df[
        [
            "date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
    ]


@log_start_end(log=logger)
def get_product_stats(symbol: str) -> pd.DataFrame:
    """Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]

    Parameters
    ----------
    symbol: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    pd.DataFrame
        24h stats for chosen trading pair
    """

    product_id = check_validity_of_product(symbol)
    product = make_coinbase_request(f"/products/{product_id}/stats")
    df = pd.Series(product).reset_index()
    df.columns = ["Metric", "Value"]
    return df
