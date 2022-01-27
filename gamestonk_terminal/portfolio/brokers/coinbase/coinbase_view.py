"""Coinbase view"""
__docformat__ = "numpy"

import os
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.portfolio.brokers.coinbase import coinbase_model
from gamestonk_terminal.rich_config import console


def display_account(currency: str = "USD", export: str = "") -> None:
    """Display list of all your trading accounts. [Source: Coinbase]

    Parameters
    ----------
    currency: str
        Currency to show current value in, default 'USD'
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_model.get_accounts(currency=currency, add_current_price=True)
    df.balance = df["balance"].astype(float)
    df = df[df.balance > 0]

    if df.empty:
        console.print("No funds/coins found in your account.")
        return

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


def display_history(account: str, export: str = "", limit: int = 20) -> None:
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
        console.print(
            f"Your account {account} doesn't have any funds or you provide wrong account name or id. "
            f"To check all your accounts use command account --all\n"
        )
        return

    print_rich_table(
        df.head(limit),
        headers=list(df.columns),
        show_index=False,
        title="Account History",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "history",
        df_data,
    )


def display_orders(limit: int, sortby: str, descend: bool, export: str = "") -> None:
    """List your current open orders [Source: Coinbase]

    Parameters
    ----------
    limit: int
        Last <limit> of trades. Maximum is 1000.
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = coinbase_model.get_orders()

    if df.empty:
        console.print("No orders found for your account\n")
        return

    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend).head(limit)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Current Open Doors",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df_data,
    )


def display_deposits(
    limit: int, sortby: str, deposit_type: str, descend: bool, export: str = ""
) -> None:
    """Display deposits into account [Source: Coinbase]

    Parameters
    ----------
    limit: int
        Last <limit> of trades. Maximum is 1000.
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descending
    deposit_type: str
        internal_deposits (transfer between portfolios) or deposit
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_deposits(deposit_type=deposit_type)

    if df.empty:
        console.print("No deposits found for your account\n")
        return

    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend).head(limit)

    print_rich_table(
        df, headers=list(df.columns), show_index=False, title="Account Deposits"
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "deposits",
        df_data,
    )
