"""Coinbase model"""
__docformat__ = "numpy"

import logging

import pandas as pd

import openbb_terminal.config_terminal as cfg
from openbb_terminal.cryptocurrency.coinbase_advanced_helpers import (
    CoinbaseAdvAuth,
    CoinbaseAdvApiException,
    make_coinbase_adv_request,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
import openbb_terminal.cryptocurrency.due_diligence.coinbase_model as cbm

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_accounts(
    add_current_price: bool = False, currency: str = "USD"
) -> pd.DataFrame:
    """Get list of all your trading accounts. [Source: Coinbase]

    Single account information:

    .. code-block:: json

    .

    Parameters
    ----------
    add_current_price: bool
        Boolean to query coinbase for current price
    currency: str
        Currency to convert to, defaults to 'USD'

    Returns
    -------
    pd.DataFrame
        DataFrame with all your trading accounts.
    """
    try:
        auth = CoinbaseAdvAuth(cfg.API_CB_ADV_KEY, cfg.API_CB_ADV_SECRET)
        resp = make_coinbase_adv_request("/accounts", auth=auth)
    except CoinbaseAdvApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if not resp:
        console.print("No data found.\n")
        return pd.DataFrame()

    # Flatten response to load into df
    flat_response = []
    resp_dict = resp["accounts"]
    for account in resp_dict:
        flat_response.append(
            {
                "id": account["uuid"],
                "name": account["name"],
                "currency": account["currency"],
                "available_balance": account["available_balance"]["value"],
                "active": account["active"],
                "hold": account["hold"]["value"],
            }
        )
    df = pd.DataFrame(flat_response)
    df = df[df.available_balance.astype(float) > 0]

    if add_current_price:
        current_prices = []
        for index, row in df.iterrows():
            _, pairs = cbm.show_available_pairs_for_given_symbol(row.currency)
            if currency not in pairs:
                df.drop(index, inplace=True)
                continue

            to_get = f"{row.currency}-{currency}"
            # Check pair validity. This is needed for delisted products like XRP
            try:
                cb_request = make_coinbase_adv_request(f"/products/{to_get}", auth=auth)
            except Exception as e:
                if "Not allowed for delisted products" in str(e):
                    message = f"Coinbase product is delisted {str(e)}"
                    logger.debug(message)
                else:
                    message = (
                        f"Coinbase does not recognize this pair {to_get}: {str(e)}"
                    )
                    logger.debug(message)

                df.drop(index, inplace=True)
                continue

            current_prices.append(float(cb_request["price"]))

        df["current_price"] = current_prices
        df[
            f"BalanceValue({currency})"
        ] = df.current_price * df.available_balance.astype(float)

        return df[
            [
                "id",
                "name",
                "currency",
                "available_balance",
                "hold",
                f"BalanceValue({currency})",
                "current_price",
            ]
        ]

    return df[["id", "name", "currency", "available_balance", "hold"]]


@log_start_end(log=logger)
def get_orders(
    limit: int = 20, sortby: str = "created_time", descend: bool = False
) -> pd.DataFrame:
    """Get a list of orders filtered by optional query parameters (product_id, order_status, etc). [Source: Coinbase]

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
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descending

    Returns
    -------
    pd.DataFrame
        Open orders in your account
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
                "type",
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
            _flat_response["type"] = "market_market_ioc"
            _flat_response["quote_size"] = _order_config["market_market_ioc"][
                "quote_size"
            ]
            _flat_response["base_size"] = _order_config["market_market_ioc"][
                "base_size"
            ]

        if "limit_limit_gtc" in _order_config:
            _flat_response["type"] = "limit_limit_gtc"
            _flat_response["limit_price"] = _order_config["limit_limit_gtc"][
                "limit_price"
            ]
            _flat_response["base_size"] = _order_config["limit_limit_gtc"]["base_size"]
            _flat_response["post_only"] = _order_config["limit_limit_gtc"]["post_only"]

        if "limit_limit_gtd" in _order_config:
            _flat_response["type"] = "limit_limit_gtd"
            _flat_response["base_size"] = _order_config["limit_limit_gtd"]["base_size"]
            _flat_response["limit_price"] = _order_config["limit_limit_gtd"][
                "limit_price"
            ]
            _flat_response["end_time"] = _order_config["limit_limit_gtd"]["end_time"]
            _flat_response["post_only"] = _order_config["limit_limit_gtd"]["post_only"]

        if "stop_limit_stop_limit_gtc" in _order_config:
            _flat_response["type"] = "stop_limit_stop_limit_gtc"
            _flat_response["base_size"] = _order_config[_flat_response["type"]][
                "base_size"
            ]
            _flat_response["limit_price"] = _order_config[_flat_response["type"]][
                "limit_price"
            ]
            _flat_response["stop_price"] = _order_config[_flat_response["type"]][
                "stop_price"
            ]
            _flat_response["stop_direction"] = _order_config[_flat_response["type"]][
                "stop_direction"
            ]

        if "stop_limit_stop_limit_gtd" in _order_config:
            _flat_response["type"] = "stop_limit_stop_limit_gtd"
            _flat_response["base_size"] = _order_config[_flat_response["type"]][
                "base_size"
            ]
            _flat_response["limit_price"] = _order_config[_flat_response["type"]][
                "limit_price"
            ]
            _flat_response["stop_price"] = _order_config[_flat_response["type"]][
                "stop_price"
            ]
            _flat_response["end_time"] = _order_config[_flat_response["type"]][
                "end_time"
            ]
            _flat_response["end_time"] = _order_config[_flat_response["type"]][
                "end_time"
            ]

        flat_response.append(_flat_response)

    df = pd.DataFrame(flat_response)
    if df.empty:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    df = df.sort_values(by=sortby, ascending=descend).head(limit)

    return df


@log_start_end(log=logger)
def get_deposits(
    limit: int = 50,
    sortby: str = "amount",
    deposit_type: str = "deposit",
    descend: bool = False,
) -> pd.DataFrame:
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
    try:
        auth = CoinbaseAdvAuth(cfg.API_CB_ADV_KEY, cfg.API_CB_ADV_SECRET)
        params = {"type": deposit_type}

        if deposit_type not in ["internal_deposit", "deposit"]:
            params["type"] = "deposit"
        resp = make_coinbase_adv_request("/transfers", auth=auth, params=params)

    except CoinbaseAdvApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if not resp:
        console.print("No deposits found for your account\n")
        return pd.DataFrame()

    if isinstance(resp, tuple):
        resp = resp[0]

    # pylint:disable=no-else-return
    if deposit_type == "deposit":
        df = pd.json_normalize(resp)
    else:
        df = pd.DataFrame(resp)[["type", "created_time", "amount", "currency"]]

    df = df.sort_values(by=sortby, ascending=descend).head(limit)
    return df
