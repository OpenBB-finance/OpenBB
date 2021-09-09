"""Coinbase model"""
__docformat__ = "numpy"

import argparse

from typing import Optional, Any, Tuple
import pandas as pd
import requests
import numpy as np


def check_validity_of_product(product_id: str) -> str:
    """Helper method that checks if provided product_id exists. It's a pair of coins in format COIN-COIN.
    If product exists it return it, in other case it raise an error. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    str
        product_id
    """

    products = [pair["id"] for pair in make_coinbase_request("/products")]
    if product_id.upper() not in products:
        raise argparse.ArgumentTypeError(
            f"You provided wrong product_id {product_id}. "
            f"It should be provided as a pair in format COIN-COIN e.g UNI-USD"
        )
    return product_id.upper()


def make_coinbase_request(
    endpoint, params: Optional[dict] = None, auth: Optional[Any] = None
) -> dict:
    """Request handler for Coinbase Pro Api. Prepare a request url, params and payload and call endpoint.
    [Source: Coinbase]

    Parameters
    ----------
    endpoint: str
        Endpoint path e.g /products
    params: dict
        Parameter dedicated for given endpoint
    auth: any
        Api credentials for purpose of using endpoints that needs authentication

    Returns
    -------
    dict
        response from Coinbase Pro Api
    """

    url = "https://api.pro.coinbase.com"
    response = requests.get(url + endpoint, params=params, auth=auth)
    if response.status_code != 200:
        raise Exception(
            f"Couldn't call the api. Status: {response.status_code} Reason: {response.reason}. "
        )
    return response.json()


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


def get_trading_pair_info(product_id: str) -> pd.DataFrame:
    """Get information about chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    pd.DataFrame
        Basic information about given trading pair
    """

    product_id = check_validity_of_product(product_id)
    pair = make_coinbase_request(f"/products/{product_id}")
    df = pd.Series(pair).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    return df


def get_order_book(product_id: str) -> Tuple[np.array, np.array, str]:
    """Get orders book for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    Tuple[np.array, np.array, str]
        array with bid prices, order sizes and cumulative order sizes
        array with ask prices, order sizes and cumulative order sizes
        trading pair
    """

    product_id = check_validity_of_product(product_id)
    market_book = make_coinbase_request(f"/products/{product_id}/book?level=2")
    bids = np.asarray(market_book["bids"], dtype=float)
    asks = np.asarray(market_book["asks"], dtype=float)
    bids = np.insert(bids, 3, (bids[:, 1] * bids[:, 2]).cumsum(), axis=1)
    asks = np.insert(asks, 3, np.flipud(asks[:, 1] * asks[:, 2]).cumsum(), axis=1)
    bids = np.delete(bids, 2, axis=1)
    asks = np.delete(asks, 2, axis=1)
    return bids, asks, product_id


def get_trades(
    product_id: str, limit: int = 1000, side: Optional[Any] = None
) -> pd.DataFrame:
    """Get last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: int
        Last <limit> of trades. Maximum is 1000.
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

    product_id = check_validity_of_product(product_id)
    product = make_coinbase_request(f"/products/{product_id}/trades", params=params)
    return pd.DataFrame(product)[["time", "price", "size", "side"]]


def get_candles(product_id: str, interval: str = "24h") -> pd.DataFrame:
    """Get candles for chosen trading pair and time interval. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1m, 5m ,15m, 1h, 6h, 24h

    Returns
    -------
    pd.DataFrame
        Candles for chosen trading pair.
    """

    intervals_map = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "1h": 3600,
        "6h": 21600,
        "24h": 86400,
    }
    if interval not in intervals_map:
        print(f"Wrong interval. Please use on from {list(intervals_map.keys())}\n")
        return pd.DataFrame()

    interval_num: int = intervals_map[interval]

    product_id = check_validity_of_product(product_id)
    candles = make_coinbase_request(
        f"/products/{product_id}/candles", params={"granularity": interval_num}
    )
    df = pd.DataFrame(candles)
    df.columns = [
        "Time0",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]
    return df


def get_product_stats(product_id: str) -> pd.DataFrame:
    """Get 24 hr stats for the product. Volume is in base currency units.
    Open, high and low are in quote currency units.  [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    pd.DataFrame
        24h stats for chosen trading pair
    """

    product_id = check_validity_of_product(product_id)
    product = make_coinbase_request(f"/products/{product_id}/stats")
    df = pd.Series(product).reset_index()
    df.columns = ["Metric", "Value"]
    return df


def get_all_currencies() -> pd.DataFrame:
    """List available currencies on Coinbase. [Source: Coinbase]

    Returns
    -------
    pd.DataFrame
        List of currencies available on Coinbase
    """

    currencies = make_coinbase_request("/currencies")
    return pd.DataFrame(
        [
            {
                "id": coin["id"],
                "name": coin["name"],
                "type": coin["details"]["type"],
            }
            for coin in currencies
        ]
    )
