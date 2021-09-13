"""Coinbase view"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.portfolio.brokers.coinbase import coinbase_model


def display_account(show_all: bool = True, export: str = "") -> None:
    """Display list of all your trading accounts. [Source: Coinbase]

    Parameters
    ----------
    show_all: bool
        Indicate if you want to show all your accounts or only one.
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    if show_all:
        df = coinbase_model.get_accounts()
    else:
        df = coinbase_model.get_accounts()
        df.balance = df["balance"].astype(float)
        df = df[df.balance > 0]

    if df.empty:
        print(
            "No funds found on you account. To display all wallets (including 0 balance) use account --all\n"
        )
        return

    df_data = df.copy()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

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
        print(
            f"Your account {account} doesn't have any funds or you provide wrong account name or id. "
            f"To check all your accounts use command account --all\n"
        )
        return

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(limit),
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.head(limit).to_string, "\n")

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
        print("No orders found for your account\n")
        return

    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend).head(limit)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "orders",
        df_data,
    )


def display_deposits(
    limit: int, sortby: str, deposite_type: str, descend: bool, export: str = ""
) -> None:
    """Display last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    limit: int
        Last <limit> of trades. Maximum is 1000.
    sortby: str
        Key to sort by
    descend: bool
        Flag to sort descending
    deposite_type: str
        internal_deposits (transfer between portfolios) or deposit
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_deposits(deposit_type=deposite_type)

    if df.empty:
        print("No deposits found for your account\n")
        return

    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend).head(limit)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "deposits",
        df_data,
    )
