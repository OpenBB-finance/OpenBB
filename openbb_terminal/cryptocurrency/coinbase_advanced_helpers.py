"""Coinbase helpers model"""
__docformat__ = "numpy"

import argparse
import binascii
import logging

from typing import Optional, Any, Union
import hmac
import hashlib
import time
import requests
from requests.auth import AuthBase
import openbb_terminal.config_terminal as cfg
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


class CoinbaseAdvAuth(AuthBase):
    """Authorize Coinbase Advanced requests. Source: https://docs.cloud.coinbase.com/advanced-trade-api"""

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = (
            timestamp
            + request.method
            + request.path_url.split("?")[0]
            + str(request.body or "")
        )
        message = message.encode("utf-8")

        try:
            signature = hmac.new(
                self.secret_key.encode("utf-8"), message, digestmod=hashlib.sha256
            ).digest()
        except binascii.Error as e:
            logger.exception(str(e))

        request.headers.update(
            {
                "CB-ACCESS-SIGN": signature.hex(),
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-KEY": self.api_key,
                "accept": "application/json",
            }
        )
        return request


class CoinbaseAdvRequestException(Exception):
    """Coinbase Request Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"CoinbaseRequestException: {self.message}"


class CoinbaseAdvApiException(Exception):
    """Coinbase API Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"CoinbaseAdvApiException: {self.message}"


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

    products = [pair["id"] for pair in make_coinbase_adv_request("/products")]
    if product_id.upper() not in products:
        raise argparse.ArgumentTypeError(
            f"You provided wrong pair of coins {product_id}. "
            f"It should be provided as a pair in format COIN-COIN e.g UNI-USD"
        )
    return product_id.upper()


def make_coinbase_adv_request(
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

    url = "https://coinbase.com/api/v3/brokerage"
    response = requests.get(url + endpoint, params=params, auth=auth)

    if not 200 <= response.status_code < 300:
        raise CoinbaseAdvApiException(f"Invalid Authentication: {response.text}")
    try:
        return response.json()
    except ValueError as e:
        logger.exception(str(e))
        raise CoinbaseAdvRequestException(f"Invalid Response: {response.text}") from e


def _get_account_coin_dict() -> dict:
    """Helper method that returns dictionary with all symbols and account ids in dictionary format. [Source: Coinbase]

    Returns
    -------
    dict:
        Your accounts in coinbase
        {'1INCH': '0c29b708-d73b-4e1c-a58c-9c261cb4bedb', 'AAVE': '0712af66-c069-45b5-84ae-7b2347c2fd24', ..}

    """
    auth = CoinbaseAdvAuth(cfg.API_COINBASE_KEY, cfg.API_COINBASE_SECRET)
    accounts = make_coinbase_adv_request("/accounts", auth=auth)
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

    console.print("Wrong account id or coin symbol")
    return None
