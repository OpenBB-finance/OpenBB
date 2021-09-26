"""Whale Alert view"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data, long_number_format
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.cryptocurrency.onchain import whale_alert_model


def display_whales_transactions(
    min_value: int = 800000,
    top: int = 100,
    sortby: str = "date",
    descend: bool = False,
    show_address: bool = False,
    export: str = "",
) -> None:
    """Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    min_value: int
        Minimum value of trade to track.
    top: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    descend: str
        Sort in descending order.
    show_address: bool
        Flag to show addresses of transactions.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = whale_alert_model.get_whales_transactions(min_value)
    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend)

    if not show_address:
        df = df.drop(["from_address", "to_address"], axis=1)
    else:
        df = df.drop(["from", "to", "blockchain"], axis=1)

    for col in ["amount_usd", "amount"]:
        df[col] = df[col].apply(lambda x: long_number_format(x))

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(top),
                headers=df.columns,
                floatfmt=".0f",
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
        "whales",
        df_data,
    )
