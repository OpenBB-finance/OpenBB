"""Coinbase model"""
__docformat__ = "numpy"

import argparse
import binascii

from typing import Optional, Any, Tuple, Union
import hmac
import hashlib
import time
import base64
import pandas as pd
import requests
import numpy as np
from requests.auth import AuthBase
import gamestonk_terminal.config_terminal as cfg


class CoinbaseProAuth(AuthBase):
    """Authorize CoinbasePro requests. Source: https://docs.pro.coinbase.com/?python#signing-a-message"""

    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or "")
        message = message.encode("ascii")

        try:
            hmac_key = base64.b64decode(self.secret_key)
            signature = hmac.new(hmac_key, message, hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest())
        except binascii.Error:
            signature_b64 = ""

        request.headers.update(
            {
                "CB-ACCESS-SIGN": signature_b64,
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-KEY": self.api_key,
                "CB-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json",
            }
        )
        return request


class CoinbaseRequestException(Exception):
    """Coinbase Request Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return "CoinbaseRequestException: %s" % self.message


class CoinbaseApiException(Exception):
    """Coinbase API Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return "CoinbaseApiException: %s" % self.message


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
        pair of coins in format COIN-COIN
    """

    products = [pair["id"] for pair in make_coinbase_request("/products")]
    if product_id.upper() not in products:
        raise argparse.ArgumentTypeError(
            f"You provided wrong pair of coins {product_id}. "
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

    if not 200 <= response.status_code < 300:
        raise CoinbaseApiException("Invalid Authentication: %s" % response.text)
    try:
        return response.json()
    except ValueError as e:
        raise CoinbaseRequestException("Invalid Response: %s" % response.text) from e


def _get_account_coin_dict() -> dict:
    """Helper method that returns dictionary with all symbols and account ids in dictionary format. [Source: Coinbase]

    Returns
    -------
    dict:
        Your accounts in coinbase
        {'1INCH': '0c29b708-d73b-4e1c-a58c-9c261cb4bedb', 'AAVE': '0712af66-c069-45b5-84ae-7b2347c2fd24', ..}

    """
    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )
    accounts = make_coinbase_request("/accounts", auth=auth)
    return {acc["currency"]: acc["id"] for acc in accounts}


def _check_account_validity(account: str) -> Union[str, Any]:
    """Helper methods that checks if given account exists. [Source: Coinbase]

    Parameters
    ----------
    account: str
        coin or account id

    Returns
    -------
    Union[str, Any]
        Your account id or None
    """

    accounts = _get_account_coin_dict()

    if account in list(accounts.keys()):
        return accounts[account]

    if account in list(accounts.values()):
        return account

    print("Wrong account id or coin symbol")
    return None


def get_accounts() -> pd.DataFrame:
    """Get list of all your trading accounts. [Source: Coinbase]

    Single account information:
    {
        "id": "71452118-efc7-4cc4-8780-a5e22d4baa53",
        "currency": "BTC",
        "balance": "0.0000000000000000",
        "available": "0.0000000000000000",
        "hold": "0.0000000000000000",
        "profile_id": "75da88c5-05bf-4f54-bc85-5c775bd68254"
    }

    Returns
    -------
    pd.DataFrame
        DataFrame with all your trading accounts.
    """

    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )
    resp = make_coinbase_request("/accounts", auth=auth)
    if not resp:
        return pd.DataFrame()
    return pd.DataFrame(resp)[["id", "currency", "balance", "available", "hold"]]


def get_account_history(account: str) -> pd.DataFrame:
    """Get your account history. Account activity either increases or decreases your account balance. [Source: Coinbase]

    Example api response:
        {
            "id": "100",
            "created_at": "2014-11-07T08:19:27.028459Z",
            "amount": "0.001",
            "balance": "239.669",
            "type": "fee",
            "details": {
                "order_id": "d50ec984-77a8-460a-b958-66f114b0de9b",
                "trade_id": "74",
                "product_id": "BTC-USD"
            }
        }


    Parameters
    ----------
    account: str
        id ("71452118-efc7-4cc4-8780-a5e22d4baa53") or currency (BTC)
    Returns
    -------
    pd.DataFrame
        DataFrame with account history.
    """

    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )

    account = _check_account_validity(account)
    if not account:
        return pd.DataFrame()

    resp = make_coinbase_request(f"/accounts/{account}/holds", auth=auth)
    if not resp:
        return pd.DataFrame()
    return pd.json_normalize(resp)


def get_account(account: str):
    """
    Parameters
    ----------
    account: str
        id ("71452118-efc7-4cc4-8780-a5e22d4baa53") or currency (BTC)

    Returns
    -------
    pd.DataFrame
        Account data
    """

    account = _check_account_validity(account)
    if not account:
        return pd.DataFrame()

    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )

    resp = make_coinbase_request(f"/accounts/{account}/holds", auth=auth)
    return pd.Series(resp).to_frame().reset_index()


def get_orders() -> pd.DataFrame:
    """List your current open orders. Only open or un-settled orders are returned. [Source: Coinbase]

    Example response from API:

    {
        "id": "d0c5340b-6d6c-49d9-b567-48c4bfca13d2",
        "price": "0.10000000",
        "size": "0.01000000",
        "product_id": "BTC-USD",
        "side": "buy",
        "stp": "dc",
        "type": "limit",
        "time_in_force": "GTC",
        "post_only": false,
        "created_at": "2016-12-08T20:02:28.53864Z",
        "fill_fees": "0.0000000000000000",
        "filled_size": "0.00000000",
        "executed_value": "0.0000000000000000",
        "status": "open",
        "settled": false
    }

    Returns
    -------
    pd.DataFrame
        Open orders in your account
    """

    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )
    resp = make_coinbase_request("/orders", auth=auth)
    if not resp:
        df = pd.DataFrame(
            columns=[
                "product_id",
                "side",
                "price",
                "size",
                "type",
                "created_at",
                "status",
            ]
        )
        return df
    return pd.DataFrame(resp)[
        ["product_id", "side", "price", "size", "type", "created_at", "status"]
    ]


def get_deposits(deposit_type: str = "deposit") -> pd.DataFrame:
    """Get a list of deposits for your account. [Source: Coinbase]

    Parameters
    ----------
    deposit_type: str
        internal_deposits (transfer between portfolios) or deposit

    Returns
    -------
    pd.DataFrame
        List of deposits
    """

    auth = CoinbaseProAuth(
        cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET, cfg.API_COINBASE_PASS_PHRASE
    )
    params = {"type": deposit_type}
    if deposit_type not in ["internal_deposit", "deposit"]:
        params["type"] = "deposit"
    resp = make_coinbase_request("/transfers", auth=auth, params=params)
    if not resp:
        return pd.DataFrame()

    if isinstance(resp, tuple):
        resp = resp[0]

    if deposit_type == "deposit":
        df = pd.json_normalize(resp)[
            [
                "type",
                "created_at",
                "amount",
                "details.crypto_address",
                "details.destination_tag_name",
            ]
        ]
        df.rename(
            columns={
                "details.crypto_address": "crypto_address",
                "details.destination_tag_name": "destination_tag",
            },
            inplace=True,
        )
    else:
        df = pd.DataFrame(resp)[["type", "created_at", "amount", "currency"]]
    return df


def show_available_pairs_for_given_symbol(symbol: str = "ETH") -> Tuple[str, list]:
    pairs = make_coinbase_request("/products")
    df = pd.DataFrame(pairs)[["base_currency", "quote_currency"]]

    if not isinstance(symbol, str):
        print(
            f"You did not provide correct symbol {symbol}. Symbol needs to be a string.\n"
        )
        return symbol, []

    coin_df = df[df["base_currency"] == symbol.upper()]
    return symbol, coin_df["quote_currency"].to_list()


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
    print(df)
    return df


def get_order_book(product_id: str) -> Tuple[np.array, np.array, str, dict]:
    """Get orders book for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    Returns
    -------
    Tuple[np.array, np.array, str, dict]
        array with bid prices, order sizes and cumulative order sizes
        array with ask prices, order sizes and cumulative order sizes
        trading pair
        dict with raw data
    """

    # TODO: Order with price much higher then current price. E.g current price 200 USD, sell order with 10000 USD
    #  makes chart look very ugly (bad scaling). Think about removing outliers or add log scale ?

    product_id = check_validity_of_product(product_id)
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
        Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour

    Returns
    -------
    pd.DataFrame
        Candles for chosen trading pair.
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
        print(f"Wrong interval. Please use on from {list(interval_map.keys())}\n")
        return pd.DataFrame()

    granularity: int = interval_map[interval]

    product_id = check_validity_of_product(product_id)
    candles = make_coinbase_request(
        f"/products/{product_id}/candles", params={"granularity": granularity}
    )
    df = pd.DataFrame(candles)
    df.columns = [
        "Time0",
        "Low",
        "High",
        "Open",
        "Close",
        "Volume",
    ]
    return df[
        [
            "Time0",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
    ]


get_candles("ETH-BTC", "1day")


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
