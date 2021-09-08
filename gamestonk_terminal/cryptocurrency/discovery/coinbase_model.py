"""Coinbase model"""
__docformat__ = "numpy"

from typing import Optional, Any
import pandas as pd
import requests
import numpy as np
from gamestonk_terminal.cryptocurrency.due_diligence.binance_model import (
    plot_order_book,
)


def _check_validity_of_product(product_id: str) -> str:
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

    products = [pair["id"] for pair in _make_coinbase_request("/products")]
    if product_id.upper() not in products:
        raise Exception(
            f"You provided wrong product_id {product_id}. "
            f"It should be provided as a pair in format COIN-COIN e.g UNI-USD"
        )
    return product_id.upper()


def _make_coinbase_request(
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


def get_products() -> pd.DataFrame:

    """
    The base_min_size and base_max_size fields define the min and max order size.
    The min_market_funds and max_market_funds fields define the min and max funds allowed in a market order.
    [Source: Coinbase]
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
        "status",
    ]
    results = _make_coinbase_request("/products")
    return pd.DataFrame(results)[columns]


def get_product(product_id: str) -> pd.DataFrame:
    """Get information about chosen product. [Source: Coinbase]

    Parameters
    ----------
    product_id

    Returns
    -------

    """
    product_id = _check_validity_of_product(product_id)
    product = _make_coinbase_request(f"/products/{product_id}")
    df = pd.Series(product).to_frame().reset_index()
    df.columns = ["Metric", "Value"]
    return df


def get_product_order_book(product_id: str):

    product_id = _check_validity_of_product(product_id)
    market_book = _make_coinbase_request(f"/products/{product_id}/book?level=2")
    bids = np.asarray(market_book["bids"], dtype=float)
    asks = np.asarray(market_book["asks"], dtype=float)

    bids = np.insert(bids, 3, (bids[:, 1] * bids[:, 2]).cumsum(), axis=1)
    asks = np.insert(asks, 3, np.flipud(asks[:, 1] * asks[:, 2]).cumsum(), axis=1)
    bids = np.delete(bids, 2, axis=1)
    asks = np.delete(asks, 2, axis=1)
    plot_order_book(bids, asks, product_id)
