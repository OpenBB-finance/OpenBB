"""Coinbase view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.portfolio.brokers.coinbase import coinbase_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_COINBASE_KEY", "API_COINBASE_SECRET", "API_COINBASE_PASS_PHRASE"])
def display_account(
    currency: str = "USD", export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display list of all your trading accounts. [Source: Coinbase]

    Parameters
    ----------
    currency: str
        Currency to show current value in, default 'USD'
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_model.get_accounts(currency=currency, add_current_price=True)

    if df.empty:
        return

    df.balance = df["balance"].astype(float)
    df = df[df.balance > 0]

    df_data = df.copy()
    df = df.drop(columns=["id"])
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="All Trading Accounts",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "account",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_COINBASE_KEY", "API_COINBASE_SECRET", "API_COINBASE_PASS_PHRASE"])
def display_history(
    account: str, export: str = "", sheet_name: Optional[str] = None, limit: int = 20
) -> None:
    """Display account history. [Source: Coinbase]

    Parameters
    ----------
    account: str
        Symbol or account id
    limit: int
        For all accounts display only top n
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_model.get_account_history(account)
    df_data = df.copy()

    if df.empty:
        return

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Account History",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "history",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_COINBASE_KEY", "API_COINBASE_SECRET", "API_COINBASE_PASS_PHRASE"])
def display_orders(
    limit: int = 20,
    sortby: str = "price",
    descend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
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
    df = coinbase_model.get_orders(limit, sortby, descend)
    df_data = df.copy()
    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Current Open Doors",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
@check_api_key(["API_COINBASE_KEY", "API_COINBASE_SECRET", "API_COINBASE_PASS_PHRASE"])
def display_deposits(
    limit: int = 20,
    sortby: str = "amount",
    deposit_type: str = "deposit",
    descend: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
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

    df = coinbase_model.get_deposits(limit, sortby, deposit_type, descend)

    if df.empty:
        return

    df_data = df.copy()

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Account Deposits",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "deposits",
        df_data,
        sheet_name,
    )
