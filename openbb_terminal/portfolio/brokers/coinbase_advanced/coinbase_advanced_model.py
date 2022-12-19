"""Coinbase model"""
__docformat__ = "numpy"

import logging
import uuid
import pandas as pd
import openbb_terminal.config_terminal as cfg
from openbb_terminal.cryptocurrency.coinbase_advanced_helpers import (
    CoinbaseAdvAuth,
    CoinbaseAdvApiException,
    make_coinbase_adv_request,
    get_all_orders,
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
    limit: int = 20,
    sortby: str = "created_time",
    descend: bool = False,
    status: str = "ALL",
) -> pd.DataFrame:
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
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descendin
    status: str
        Status of the order

    Returns
    -------
    pd.DataFrame
        Open orders in your account
    """

    try:
        df = get_all_orders(limit=limit)
    except CoinbaseAdvApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    if status != "ALL":
        df = df[df["status"] == status]
    df = df.sort_values(by=sortby, ascending=descend).head(limit)

    return df


@log_start_end(log=logger)
def create_order(
    product_id: str = "",
    side: str = "",
    dry_run: bool = False,
    order_type: str = "",
    **kwargs,
) -> pd.DataFrame:
    """
    Place an order. [Source: Coinbase]
    https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder
    Example response from API:

    .. code-block:: json
        {
          "success": "boolean",
          "failure_reason": "string",
          "order_id": "string",
          "success_response": "object",
          "error_response": "object",
          "order_configuration": "object"
        }{
          "success": "boolean",
          "failure_reason": "string",
          "order_id": "string",
          "success_response": "object",
          "error_response": "object",
          "order_configuration": "object"
        }
    .
    Parameters
    ----------
    dry_run: bool
        If set to True, display order payload, but do not submit to Coinbase
    product_id: string
        The product this order was created for e.g. 'BTC-USD'
    side: string
        Possible values: [UNKNOWN_ORDER_SIDE, BUY, SELL]
    order_type: basestring
        Type of order : [market_market_ioc, limit_limit_gtc, limit_limit_gtd,
        stop_limit_stop_limit_gtc, stop_limit_stop_limit_gtd ]
    quote_size: float
        Amount of quote currency to spend on order. Required for BUY orders.
        Required for type: market_market_ioc
    base_size: float
        Amount of base currency to spend on order. Required for SELL orders.
        Required for type: market_market_ioc
    limit_price: float
        Ceiling price for which the order should get filled
        Required for type: limit_limit_gtc, limit_limit_gtd, stop_limit_stop_limit_gtc, stop_limit_stop_limit_gtd
    end_time: int
        Time at which the order should be cancelled if it's not filled.
        Required for type: limit_limit_gtd, stop_limit_stop_limit_gtd
    post_only: bool
        Post only limit order
        Required for type: limit_limit_gtd, limit_limit_gtc
    stop_price: float
        Price at which the order should trigger - if stop direction is Up, then the order
         will trigger when the last trade price goes above this, otherwise order will
         trigger when last trade price goes below this price.
        Requited for type: stop_limit_stop_limit_gtc,  stop_limit_stop_limit_gtd
    stop_direction: string
        Possible values: [UNKNOWN_STOP_DIRECTION, STOP_DIRECTION_STOP_UP, STOP_DIRECTION_STOP_DOWN]
        Required for type: stop_limit_stop_limit_gtd, stop_limit_stop_limit_gtc
    dry_run: bool
        Show payload without placing order

    Returns
    -------

    """
    quote_size = kwargs.get("quote_size", 0)
    base_size = kwargs.get("base_size", 0)
    limit_price = kwargs.get("limit_price", 0)
    end_time = kwargs.get("end_time", 0)
    post_only = kwargs.get("post_only", True)
    stop_price = kwargs.get("stop_price", 0)
    stop_direction = kwargs.get("stop_direction", "")

    order_payload: dict = {}
    order_payload["order_configuration"] = {}
    type_payload = {}
    if order_type == "market_market_ioc":
        if side == "BUY":
            type_payload["quote_size"] = str(quote_size)
        if side == "SELL":
            type_payload["base_size"] = str(base_size)

    if order_type == "limit_limit_gtc":
        type_payload["limit_price"] = str(limit_price)
        type_payload["base_size"] = str(base_size)
        type_payload["post_only"] = post_only

    if order_type == "limit_limit_gtd":
        type_payload["base_size"] = str(base_size)
        type_payload["limit_price"] = str(limit_price)
        type_payload["end_time"] = str(end_time)
        type_payload["post_only"] = post_only

    if order_type == "stop_limit_stop_limit_gtc":
        type_payload["base_size"] = str(base_size)
        type_payload["limit_price"] = str(limit_price)
        type_payload["stop_price"] = str(stop_price)
        type_payload["stop_direction"] = stop_direction

    if order_type == "stop_limit_stop_limit_gtd":
        type_payload["base_size"] = str(base_size)
        type_payload["limit_price"] = str(limit_price)
        type_payload["stop_price"] = str(stop_price)
        type_payload["end_time"] = str(end_time)
        type_payload["stop_direction"] = stop_direction

    order_payload["order_configuration"][order_type] = type_payload
    order_payload["client_order_id"] = str(uuid.uuid4())
    order_payload["product_id"] = product_id
    order_payload["side"] = side

    response_dict = {}

    if bool(dry_run):
        response_dict["status"] = "Dry Run"
        response_dict["order_type"] = order_type
        response_dict["order_configuration"] = order_payload["order_configuration"]
        response_dict["product_id"] = order_payload["product_id"]
        response_dict["side"] = order_payload["side"]
        return pd.DataFrame(response_dict)

    try:
        auth = CoinbaseAdvAuth(cfg.API_CB_ADV_KEY, cfg.API_CB_ADV_SECRET)
        resp = make_coinbase_adv_request(
            "/orders", method="post", params=order_payload, auth=auth
        )

    except CoinbaseAdvApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)
        return pd.DataFrame()

    response_dict["Status"] = "Success" if resp["success"] else "Failed"
    if resp["success"]:
        response_dict["Order"] = resp["order_id"]
        response_dict["success_response"] = resp["success_response"]
    else:
        response_dict["Failure"] = resp["failure_reason"]
        response_dict["error_response"] = resp["error_response"]

    df = pd.DataFrame(response_dict)
    if df.empty:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    # df = df.sort_values(by=sortby, ascending=descend).head(limit)

    return df


@log_start_end(log=logger)
def cancel_order(
    order_id: str = "",
) -> pd.DataFrame:
    """
        Place an order. [Source: Coinbase]
        https://docs.cloud.coinbase.com/advanced-trade-api/reference/retailbrokerageapi_postorder
        Example response from API:
        {
      "results": {[
        "success": true,
        "failure_reason": "UNKNOWN_CANCEL_FAILURE_REASON",
        "order_id": "0000-00000"],
      }
    }
        Parameters
        ----------
        order_id: str
            Coinbase Advanced order_id
        Returns
        -------

    """

    order_cancel_payload = {"order_ids": [order_id]}

    try:
        auth = CoinbaseAdvAuth(cfg.API_CB_ADV_KEY, cfg.API_CB_ADV_SECRET)
        resp = make_coinbase_adv_request(
            "/orders/batch_cancel",
            method="post",
            params=order_cancel_payload,
            auth=auth,
        )

    except CoinbaseAdvApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)
        return pd.DataFrame()

    response_dict = {}
    response_dict["Status"] = "Success" if resp["results"][0]["success"] else "Failed"
    response_dict["response"] = resp["results"]

    df = pd.DataFrame(response_dict)
    if df.empty:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    return df
