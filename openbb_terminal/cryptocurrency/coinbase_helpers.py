"""Coinbase helpers model"""
__docformat__ = "numpy"

import argparse
import base64
import binascii
import hashlib
import hmac
import logging
import time
from typing import Any, Optional, Union

from requests.auth import AuthBase

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


class CoinbaseProAuth(AuthBase):
    """Authorize CoinbasePro requests. Source: https://docs.pro.coinbase.com/?python#signing-a-message"""

    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request_coinbase):
        timestamp = str(time.time())
        message = (
            timestamp
            + request_coinbase.method
            + request_coinbase.path_url
            + (request_coinbase.body or "")
        )
        message = message.encode("ascii")

        try:
            hmac_key = base64.b64decode(self.secret_key)
            signature = hmac.new(hmac_key, message, hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest())
        except binascii.Error as e:
            logger.exception(str(e))
            signature_b64 = ""

        request_coinbase.headers.update(
            {
                "CB-ACCESS-SIGN": signature_b64,
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-KEY": self.api_key,
                "CB-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json",
            }
        )
        return request_coinbase


class CoinbaseRequestException(Exception):
    """Coinbase Request Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"CoinbaseRequestException: {self.message}"


class CoinbaseApiException(Exception):
    """Coinbase API Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"CoinbaseApiException: {self.message}"


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
    response = request(url + endpoint, params=params, auth=auth)

    if not 200 <= response.status_code < 300:
        raise CoinbaseApiException(f"Invalid Authentication: {response.text}")
    try:
        return response.json()
    except ValueError as e:
        logger.exception(str(e))
        raise CoinbaseRequestException(f"Invalid Response: {response.text}") from e


def _get_account_coin_dict() -> dict:
    """Helper method that returns dictionary with all symbols and account ids in dictionary format. [Source: Coinbase]

    Returns
    -------
    dict:
        Your accounts in coinbase
        {'1INCH': '0c29b708-d73b-4e1c-a58c-9c261cb4bedb', 'AAVE': '0712af66-c069-45b5-84ae-7b2347c2fd24', ..}

    """
    current_user = get_current_user()
    auth = CoinbaseProAuth(
        current_user.credentials.API_COINBASE_KEY,
        current_user.credentials.API_COINBASE_SECRET,
        current_user.credentials.API_COINBASE_PASS_PHRASE,
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

    console.print("Wrong account id or coin symbol")
    return None
