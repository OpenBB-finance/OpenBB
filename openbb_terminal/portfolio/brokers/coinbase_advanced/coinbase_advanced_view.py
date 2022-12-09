"""Coinbase view"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.decorators import check_api_key
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.portfolio.brokers.coinbase_advanced import coinbase_advanced_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_CB_ADV_KEY", "API_CB_ADV_SECRET"])
def display_account(currency: str = "USD", export: str = "") -> None:
    """Display list of all your trading accounts. [Source: Coinbase]

    Parameters
    ----------
    currency: str
        Currency to show current value in, default 'USD'
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_advanced_model.get_accounts(currency=currency, add_current_price=True)

    if df.empty:
        return

    df.available_balance = df["available_balance"].astype(float)
    df = df[df.available_balance > 0]

    df_data = df.copy()
    df = df.drop(columns=["id"])
    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="All Trading Accounts"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "account",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_CB_ADV_KEY", "API_CB_ADV_SECRET"])
def display_orders(
    limit: int = 20,
    sortby: str = "created_time",
    descend: bool = False,
    export: str = "",
) -> None:
    """List your current open orders [Source: Coinbase]

    Parameters
    ----------
    limit: int
        Last `limit` of trades. Maximum is 1000.
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_advanced_model.get_orders(limit, sortby, descend)
    df_data = df.copy()
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Current Open Doors",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df_data,
    )


@log_start_end(log=logger)
@check_api_key(["API_CB_ADV_KEY", "API_CB_ADV_SECRET"])
def display_deposits(
    limit: int = 20,
    sortby: str = "amount",
    deposit_type: str = "deposit",
    descend: bool = False,
    export: str = "",
) -> None:
    """Display deposits into account [Source: Coinbase]

    Parameters
    ----------
    limit: int
        Last `limit` of trades. Maximum is 1000.
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descending
    deposit_type: str
        internal_deposits (transfer between portfolios) or deposit
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_advanced_model.get_deposits(limit, sortby, deposit_type, descend)

    if df.empty:
        return

    df_data = df.copy()

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Account Deposits"
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "deposits",
        df_data,
    )
