"""Gemini model"""
__docformat__ = "numpy"

import logging
import uuid
import pandas as pd
from dotenv import get_key
import openbb_terminal.config_terminal as cfg
from openbb_terminal.base_helpers import strtobool
import openbb_terminal.feature_flags as obbff
from openbb_terminal.cryptocurrency.gemini_helpers import (
    GeminiAuth,
    GeminiApiException,
    GeminiFunctions,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_accounts(limit: int = 499) -> pd.DataFrame:
    """Get accounts in Master group [Source: Gemini]
    https://docs.gemini.com/rest-api/#get-accounts-in-master-group


    Parameters
    ----------
    limit: int
        limit on number of returned values

    Returns
    -------
    pd.DataFrame
        DataFrame with all your accounts.
    """
    try:
        auth = GeminiAuth(cfg.API_GEMINI_KEY, cfg.API_GEMINI_SECRET)
        resp = GeminiFunctions().make_gemini_request(
            "account/list", params={"limit_accounts": limit}, auth=auth
        )
    except GeminiApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if not resp:
        console.print("No data found.\n")
        return pd.DataFrame()

    df = pd.DataFrame(resp)

    return df


@log_start_end(log=logger)
def get_orders(
    limit: int = 20,
    sortby: str = "timestamp",
    descend: bool = False,
    status: str = "all",
) -> pd.DataFrame:
    """
    Parameters
    ----------
    limit: int
        Last `limit` of trades. Maximum is 1000.
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descendin
    status: str
        Status filter for order

    Returns
    -------
    pd.DataFrame
        Open orders in your account
    """
    try:
        df = GeminiFunctions().get_all_orders()
    except GeminiApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    if status != "all":
        df = df[df[status] is True]

    return df.sort_values(by=sortby, ascending=descend).head(limit)


@log_start_end(log=logger)
def create_order(
    symbol: str = "",
    side: str = "",
    amount: float = 0,
    price: float = 0,
    order_type: str = "",
    stop_price: float = 0,
    account: str = "primary",
    options: str = None,
) -> pd.DataFrame:

    order_payload: dict = {}
    order_payload["client_order_id"] = str(uuid.uuid4())
    order_payload["symbol"] = symbol
    order_payload["side"] = side
    order_payload["amount"] = str(amount)
    order_payload["price"] = str(price)
    order_payload["type"] = order_type
    order_payload["account"] = account
    if stop_price != 0 and stop_price is not None:
        order_payload["stop_price"] = str(stop_price)
    elif options is not None:
        order_payload["options"] = [options]

    if strtobool(get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_DRYRUN") or "False"):
        return pd.DataFrame(order_payload, index=[0])

    try:
        auth = GeminiAuth(cfg.API_GEMINI_KEY, cfg.API_GEMINI_SECRET)
        resp = GeminiFunctions().make_gemini_request(
            "order/new", method="post", params=order_payload, auth=auth
        )

    except GeminiApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)
        return pd.DataFrame()

    df = pd.DataFrame([resp])
    if df.empty:
        return pd.DataFrame()

    return df


@log_start_end(log=logger)
def cancel_orders(
    order_id: str = None, all_active: bool = None, account: str = "primary"
) -> pd.DataFrame:

    order_cancel_payload = {"account": account}
    if all_active:
        request_path = "order/cancel/all"
    elif order_id is not None:
        request_path = "order/cancel"
        order_cancel_payload["order_id"] = order_id
    else:
        console.print("[red]No order provided[/red]\n")
        return pd.DataFrame()

    # Dry-Run returns payload
    if strtobool(get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_DRYRUN") or "False"):
        return pd.DataFrame(order_cancel_payload)

    try:
        auth = GeminiAuth(cfg.API_GEMINI_KEY, cfg.API_GEMINI_SECRET)
        resp = GeminiFunctions().make_gemini_request(
            request_path,
            method="post",
            params=order_cancel_payload,
            auth=auth,
        )
    except GeminiApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)
        return pd.DataFrame()
    response_dict = {}

    if all_active:
        response_dict["result"] = resp["result"]
        response_dict["cancelRejects"] = resp["details"]["cancelRejects"]
        response_dict["cancelledOrders"] = resp["details"]["cancelledOrders"]
    else:
        resp["options"] = resp["options"]
        response_dict = resp

    df = pd.DataFrame([response_dict])
    if df.empty:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    return df
