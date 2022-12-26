"""Coinbase helpers model"""
__docformat__ = "numpy"

import argparse
import binascii
import logging

from typing import Optional, Any, Union
from datetime import datetime, timezone
import hmac
import hashlib
import time
import json
import requests
import pytz
import pandas as pd
from requests.auth import AuthBase
import openbb_terminal.config_terminal as cfg
from openbb_terminal.rich_config import console
from openbb_terminal.helper_funcs import valid_datetime


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


class DateTimeAction(argparse.Action):
    """Convert datetime entered by user from
    local timezone to UTC in ISO 8601 format.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        date_parsed = valid_datetime(
            # "%Y-%m-%dT%I:%M:00Z"
            values,
            input_format="%d-%m-%Y_%I:%M_%p",
        )
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        date_with_tz = date_parsed.replace(tzinfo=local_tz)
        date_utc = date_with_tz.astimezone(pytz.utc).isoformat()
        setattr(namespace, self.dest, date_utc)


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
    auth = CoinbaseAdvAuth(cfg.API_CB_ADV_KEY, cfg.API_CB_ADV_SECRET)
    products = [
        pair["product_id"]
        for pair in make_coinbase_adv_request("/products", auth=auth)["products"]
    ]
    if product_id.upper() not in products:
        raise argparse.ArgumentTypeError(
            f"You provided wrong pair of coins {product_id}. "
            f"It should be provided as a pair in format COIN-COIN e.g UNI-USD"
        )
    return product_id.upper()


def make_coinbase_adv_request(
    endpoint,
    params: Optional[dict] = None,
    auth: Optional[Any] = None,
    method: str = "get",
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
    method: basestring
        Http method [post, get]

    Returns
    -------
    dict
        response from Coinbase Pro Api
    """

    url = "https://coinbase.com/api/v3/brokerage"
    if method == "get":
        response = requests.get(url + endpoint, params=params, auth=auth)
    else:
        response = requests.post(url + endpoint, data=json.dumps(params), auth=auth)

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


def get_all_orders(limit: int = 1000) -> pd.DataFrame:
    """Get a list of orders filtered by optional query parameters (product_id, order_status, etc). [Source: Coinbase]
    https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_gethistoricalorders
    Example response from API:

    .. code-block:: json

                {
                  "orders": [
                    {
                      "order_id": "0000-000000-000000",
                      "product_id": "BTC-USD",
                      "user_id": "2222-000000-000000",
                      "order_configuration": {
                        "market_market_ioc": {
                          "quote_size": "10.00",
                          "base_size": "0.001"
                        },
                        "limit_limit_gtc": {
                          "base_size": "0.001",
                          "limit_price": "10000.00",
                          "post_only": false
                        },
                        "limit_limit_gtd": {
                          "base_size": "0.001",
                          "limit_price": "10000.00",
                          "end_time": "2021-05-31T09:59:59Z",
                          "post_only": false
                        },
                        "stop_limit_stop_limit_gtc": {
                          "base_size": "0.001",
                          "limit_price": "10000.00",
                          "stop_price": "20000.00",
                          "stop_direction": "UNKNOWN_STOP_DIRECTION"
                        },
                        "stop_limit_stop_limit_gtd": {
                          "base_size": 0.001,
                          "limit_price": "10000.00",
                          "stop_price": "20000.00",
                          "end_time": "2021-05-31T09:59:59Z",
                          "stop_direction": "UNKNOWN_STOP_DIRECTION"
                        }
                      },
                      "side": "UNKNOWN_ORDER_SIDE",
                      "client_order_id": "11111-000000-000000",
                      "status": "OPEN",
                      "time_in_force": "UNKNOWN_TIME_IN_FORCE",
                      "created_time": "2021-05-31T09:59:59Z",
                      "completion_percentage": "50",
                      "filled_size": "0.001",
                      "average_filled_price": "50",
                      "fee": "string",
                      "number_of_fills": "2",
                      "filled_value": "10000",
                      "pending_cancel": true,
                      "size_in_quote": false,
                      "total_fees": "5.00",
                      "size_inclusive_of_fees": false,
                      "total_value_after_fees": "string",
                      "trigger_status": "UNKNOWN_TRIGGER_STATUS",
                      "order_type": "UNKNOWN_ORDER_TYPE",
                      "reject_reason": "REJECT_REASON_UNSPECIFIED",
                      "settled": true,
                      "product_type": "UNKNOWN_PRODUCT_TYPE",
                      "reject_message": "string",
                      "cancel_message": "string"
                    }
                  ],
                  "sequence": "string",
                  "has_next": true,
                  "cursor": "789100"
                }

    .
    Parameters
    ----------
    limit: int
        Last `limit` of trades. Maximum is 1000.

    Returns
    -------
    pd.DataFrame
        All orders in your account
    """

    try:
        auth = CoinbaseAdvAuth(cfg.API_CB_ADV_KEY, cfg.API_CB_ADV_SECRET)
        resp = make_coinbase_adv_request(
            "/orders/historical/batch", params={"limit": limit}, auth=auth
        )

    except CoinbaseAdvApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if not resp:
        console.print("No orders found for your account\n")

        return pd.DataFrame(
            columns=[
                "product_id",
                "side",
                "price",
                "size",
                "order_type",
                "created_time",
                "status",
            ]
        )

    # Flatten response to load into df
    flat_response = []
    resp_dict = resp["orders"]
    for orders in resp_dict:
        _flat_response = {
            "order_id": orders["order_id"],
            "product_id": orders["product_id"],
            "created_time": orders["created_time"],
            "side": orders["side"],
            "status": orders["status"],
            "fee": orders["fee"],
        }
        # Handle parsing for diff ordee types
        _order_config = orders["order_configuration"]

        if "market_market_ioc" in _order_config:
            _flat_response["order_type"] = "market_market_ioc"
            _flat_response["quote_size"] = _order_config["market_market_ioc"][
                "quote_size"
            ]
            _flat_response["base_size"] = _order_config["market_market_ioc"][
                "base_size"
            ]

        if "limit_limit_gtc" in _order_config:
            _flat_response["order_type"] = "limit_limit_gtc"
            _flat_response["limit_price"] = _order_config["limit_limit_gtc"][
                "limit_price"
            ]
            _flat_response["base_size"] = _order_config["limit_limit_gtc"]["base_size"]
            _flat_response["post_only"] = _order_config["limit_limit_gtc"]["post_only"]

        if "limit_limit_gtd" in _order_config:
            _flat_response["order_type"] = "limit_limit_gtd"
            _flat_response["base_size"] = _order_config["limit_limit_gtd"]["base_size"]
            _flat_response["limit_price"] = _order_config["limit_limit_gtd"][
                "limit_price"
            ]
            _flat_response["end_time"] = _order_config["limit_limit_gtd"]["end_time"]
            _flat_response["post_only"] = _order_config["limit_limit_gtd"]["post_only"]

        if "stop_limit_stop_limit_gtc" in _order_config:
            _flat_response["order_type"] = "stop_limit_stop_limit_gtc"
            _flat_response["base_size"] = _order_config[_flat_response["order_type"]][
                "base_size"
            ]
            _flat_response["limit_price"] = _order_config[_flat_response["order_type"]][
                "limit_price"
            ]
            _flat_response["stop_price"] = _order_config[_flat_response["order_type"]][
                "stop_price"
            ]
            _flat_response["stop_direction"] = _order_config[
                _flat_response["order_type"]
            ]["stop_direction"]

        if "stop_limit_stop_limit_gtd" in _order_config:
            _flat_response["order_type"] = "stop_limit_stop_limit_gtd"
            _flat_response["base_size"] = _order_config[_flat_response["order_type"]][
                "base_size"
            ]
            _flat_response["limit_price"] = _order_config[_flat_response["order_type"]][
                "limit_price"
            ]
            _flat_response["stop_price"] = _order_config[_flat_response["order_type"]][
                "stop_price"
            ]
            _flat_response["end_time"] = _order_config[_flat_response["order_type"]][
                "end_time"
            ]
            _flat_response["end_time"] = _order_config[_flat_response["order_type"]][
                "end_time"
            ]

        flat_response.append(_flat_response)

    df = pd.DataFrame(flat_response)
    if df.empty:
        return pd.DataFrame()

    return df


def get_order_id_list(status="OPEN") -> list:
    """
    Parameters
    ----------
    status: str
        Order status to filter list

    Returns
    -------
    List of order ids matching status
    """
    order_list = get_all_orders()
    df = order_list[order_list["status"] == status]
    order_id_list = df["order_id"].to_dict()
    return_list = []
    for order_id in order_id_list.keys():
        return_list.append(order_id_list[order_id])
    return return_list
