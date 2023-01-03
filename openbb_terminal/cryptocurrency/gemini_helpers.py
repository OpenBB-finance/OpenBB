"""Gemini helpers model"""
__docformat__ = "numpy"

import argparse
import binascii
import logging

from typing import Optional, Any, Union
from datetime import datetime, timezone
import hmac
import hashlib
import time
import base64
import json
import requests
import pytz
import pandas as pd
from dotenv import get_key
from requests.auth import AuthBase
from openbb_terminal.base_helpers import strtobool
import openbb_terminal.config_terminal as cfg
from openbb_terminal import feature_flags as obbff
from openbb_terminal.rich_config import console
from openbb_terminal.helper_funcs import valid_datetime


logger = logging.getLogger(__name__)


class GeminiAuth(AuthBase):
    """Authorize Gemini  requests. Source: https://docs.gemini.com/rest-api/?python#private-api-invocation"""

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        payload_nonce = time.time()
        payload = {
            "request": f"{request.path_url.split('?')[0]}",
            "nonce": payload_nonce,
            **json.loads(request.body),
        }
        payloadb64 = base64.b64encode(json.dumps(payload).encode())
        try:
            signature = hmac.new(
                self.secret_key.encode(), payloadb64, digestmod=hashlib.sha384
            ).hexdigest()
        except binascii.Error as e:
            logger.exception(str(e))

        request.headers.update(
            {
                "Content-Type": "text/plain",
                "X-GEMINI-SIGNATURE": signature,
                "X-GEMINI-APIKEY": self.api_key,
                "X-GEMINI-PAYLOAD": payloadb64,
                "Cache-Control": "no-cache",
            }
        )
        return request


class GeminiRequestException(Exception):
    """Gemini Request Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"GeminiRequestException: {self.message}"


class GeminiApiException(Exception):
    """Gemini API Exception object"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"GeminiApiException: {self.message}"


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


def check_validity_of_symbol(symbol: str) -> str:
    """Helper method that checks if provided product_id exists. It's a pair of coins in format COIN-COIN.
    If product exists it return it, in other case it raise an error. [Source: Gemini]

    Parameters
    ----------
    symbol: str
        Trading symbol on Gemini e.g btcusd, ethusd

    Returns
    -------
    str
        pair of coins in format COIN-COIN
    """
    auth = GeminiAuth(cfg.API_GEMINI_KEY, cfg.API_GEMINI_SECRET)
    gmf = GeminiFunctions()
    symbols = (
        symbol
        for symbol in gmf.make_gemini_request("/symbols", auth=auth, method="get")
    )
    if symbol not in symbols:
        raise argparse.ArgumentTypeError(
            f"You provided wrong pair of coins {symbol}. "
            f"It should be provided as a pair in format coincoin or coinusd e.g btcusd"
        )
    return symbol


class GeminiFunctions:
    def __init__(self):
        self.sandbox = strtobool(
            get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_SANDBOX") or "False"
        )
        self.account = (
            get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_ACCOUNT") or "Primary"
        )

    def make_gemini_request(
        self,
        endpoint,
        params: Optional[dict] = None,
        auth: Optional[Any] = None,
        method: str = "post",
    ) -> dict:
        """Request handler for Gemini Pro Api. Prepare a request url, params and payload and call endpoint.
        [Source: Gemini]

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
            response from Gemini Api
        """
        if self.sandbox:
            url = "https://api.sandbox.gemini.com/v1/"
        else:
            url = "https://api.gemini.com/v1/"

        if method == "get":
            response = requests.get(url + endpoint, params=params)
        else:
            response = requests.post(url + endpoint, data=json.dumps(params), auth=auth)

        if not 200 <= response.status_code < 300:
            raise GeminiApiException(f"Invalid Authentication: {response.text}")
        try:
            return response.json()
        except ValueError as e:
            logger.exception(str(e))
            raise GeminiRequestException(f"Invalid Response: {response.text}") from e

    def _get_account_dict(self) -> dict:
        """Helper method that returns dictionary with all Gemini accounts
        Parameters
        __________
            sandbox: bool
                Run in Gemini Sandbox
            Returns
            -------
            dict:
                Your accounts in Gemini
                {'primary': 'Primary', 'my-custody-account': 'My Custody Account', ..}

        """
        auth = GeminiAuth(cfg.API_GEMINI_KEY, cfg.API_GEMINI_SECRET)
        accounts = self.make_gemini_request(
            "account/list", params={"limit_accounts": 100}, auth=auth
        )
        return {acc["account"]: acc["name"] for acc in accounts}

    def check_account_validity(self, account: str) -> Union[str, Any]:
        """Helper methods that checks if given account exists. [Source: Gemini]

        Parameters
        ----------
        account: str
            coin or account id

        Returns
        -------
        Union[str, Any]
            Your account id or None
        """

        accounts = self._get_account_dict()

        if account in list(accounts.keys()):
            return account

        console.print(f"Wrong account id  {account}")
        return None

    def get_all_orders(self) -> pd.DataFrame:
        """Get Active Orders
                https://docs.gemini.com/rest-api/#get-active-orders
                Example response from API:
        [   {
            "order_id": "107421210",
            "id": "107421210",
            "symbol": "ethusd",
            "exchange": "gemini",
            "avg_execution_price": "0.00",
            "side": "sell",
            "type": "exchange limit",
            "timestamp": "1547241628",
            "timestampms": 1547241628042,
            "is_live": True,
            "is_cancelled": False,
            "is_hidden": False,
            "was_forced": False,
            "executed_amount": "0",
            "remaining_amount": "1",
            "options": [],
            "price": "125.51",
            "original_amount": "1"
          },
          ]
                Parameters
                ----------

                Returns
                -------
                pd.DataFrame
                    All orders in your account
        """
        _df_columns = [
            "order_id",
            "symbol",
            "exchange",
            "timestamp",
            "side",
            "price",
            "type",
            "options",
            "is_live",
            "is_cancelled",
        ]
        try:
            auth = GeminiAuth(cfg.API_GEMINI_KEY, cfg.API_GEMINI_SECRET)
            resp = self.make_gemini_request(
                "orders", params={"account": self.account}, auth=auth
            )

        except GeminiApiException as e:
            if "Invalid API Key" in str(e):
                console.print("[red]Invalid API Key[/red]\n")
            else:
                console.print(e)

            return pd.DataFrame()

        if not resp:
            console.print("No orders found for your account\n")

            return pd.DataFrame(columns=_df_columns)

        df = pd.DataFrame(resp)
        if df.empty:
            return pd.DataFrame()

        return df[_df_columns]

    def get_order_id_list(self, is_live=True) -> list:
        """
                Parameters
                ----------
                is_live: bool
        true if the order is active on the book (has remaining quantity and has not been canceled)
                Returns
                -------
                List of order ids matching status
        """
        order_list = self.get_all_orders()
        df = order_list[order_list["is_live"] == is_live]
        order_id_list = df["order_id"].to_dict()
        return_list = []
        for order_id in order_id_list.keys():
            return_list.append(order_id_list[order_id])
        return return_list
