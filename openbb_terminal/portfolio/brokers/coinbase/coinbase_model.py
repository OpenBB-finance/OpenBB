"""Coinbase model"""
__docformat__ = "numpy"

import logging

import pandas as pd

import openbb_terminal.cryptocurrency.due_diligence.coinbase_model as cbm
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.coinbase_helpers import (
    CoinbaseApiException,
    CoinbaseProAuth,
    _check_account_validity,
    make_coinbase_request,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_accounts(add_current_price: bool = True, currency: str = "USD") -> pd.DataFrame:
    """Get list of all your trading accounts. [Source: Coinbase]

    Single account information:

    .. code-block:: json

        {
            "id": "71452118-efc7-4cc4-8780-a5e22d4baa53",
            "currency": "BTC",
            "balance": "0.0000000000000000",
            "available": "0.0000000000000000",
            "hold": "0.0000000000000000",
            "profile_id": "75da88c5-05bf-4f54-bc85-5c775bd68254"
        }

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
    current_user = get_current_user()
    try:
        auth = CoinbaseProAuth(
            current_user.credentials.API_COINBASE_KEY,
            current_user.credentials.API_COINBASE_SECRET,
            current_user.credentials.API_COINBASE_PASS_PHRASE,
        )
        resp = make_coinbase_request("/accounts", auth=auth)
    except CoinbaseApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if not resp:
        console.print("No data found.\n")
        return pd.DataFrame()

    df = pd.DataFrame(resp)

    df = df[df.balance.astype(float) > 0]

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
                cb_request = make_coinbase_request(
                    f"/products/{to_get}/stats", auth=auth
                )
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

            current_prices.append(float(cb_request["last"]))

        df["current_price"] = current_prices
        df[f"BalanceValue({currency})"] = df.current_price * df.balance.astype(float)

        return df[
            [
                "id",
                "currency",
                "balance",
                "available",
                "hold",
                f"BalanceValue({currency})",
            ]
        ]
    return df[["id", "currency", "balance", "available", "hold"]]


@log_start_end(log=logger)
def get_account_history(account: str) -> pd.DataFrame:
    """Get your account history. Account activity either increases or decreases your account balance. [Source: Coinbase]

    Example api response:

    .. code-block:: json

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

    .

    Parameters
    ----------
    account: str
        id ("71452118-efc7-4cc4-8780-a5e22d4baa53") or currency (BTC)
    Returns
    -------
    pd.DataFrame
        DataFrame with account history.
    """
    current_user = get_current_user()
    try:
        auth = CoinbaseProAuth(
            current_user.credentials.API_COINBASE_KEY,
            current_user.credentials.API_COINBASE_SECRET,
            current_user.credentials.API_COINBASE_PASS_PHRASE,
        )

        account = _check_account_validity(account)
        resp = make_coinbase_request(f"/accounts/{account}/holds", auth=auth)

    except CoinbaseApiException as e:
        if "Invalid API Key" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(e)

        return pd.DataFrame()

    if not account:
        console.print(f"Account {account} not exist.\n")
        return pd.DataFrame()

    if not resp:
        console.print(
            f"Your account {account} doesn't have any funds."
            f"To check all your accounts use command account --all\n"
        )
        return pd.DataFrame()

    df = pd.json_normalize(resp)

    try:
        df.columns = [
            col.replace("details.", "") if "details" in col else col
            for col in df.columns
        ]
    except Exception as e:
        logger.exception(str(e))
        console.print(e)

    return df


@log_start_end(log=logger)
def get_orders(
    limit: int = 20, sortby: str = "price", descend: bool = False
) -> pd.DataFrame:
    """List your current open orders. Only open or un-settled orders are returned. [Source: Coinbase]

    Example response from API:

    .. code-block:: json

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
    current_user = get_current_user()
    try:
        auth = CoinbaseProAuth(
            current_user.credentials.API_COINBASE_KEY,
            current_user.credentials.API_COINBASE_SECRET,
            current_user.credentials.API_COINBASE_PASS_PHRASE,
        )
        resp = make_coinbase_request("/orders", auth=auth)

    except CoinbaseApiException as e:
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
                "created_at",
                "status",
            ]
        )

    df = pd.DataFrame(resp)
    if df.empty:
        return pd.DataFrame()
    df = df[["product_id", "side", "price", "size", "type", "created_at", "status"]]

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
    current_user = get_current_user()
    try:
        auth = CoinbaseProAuth(
            current_user.credentials.API_COINBASE_KEY,
            current_user.credentials.API_COINBASE_SECRET,
            current_user.credentials.API_COINBASE_PASS_PHRASE,
        )
        params = {"type": deposit_type}

        if deposit_type not in ["internal_deposit", "deposit"]:
            params["type"] = "deposit"
        resp = make_coinbase_request("/transfers", auth=auth, params=params)

    except CoinbaseApiException as e:
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
        df = pd.DataFrame(resp)[["type", "created_at", "amount", "currency"]]

    df = df.sort_values(by=sortby, ascending=descend).head(limit)
    return df
