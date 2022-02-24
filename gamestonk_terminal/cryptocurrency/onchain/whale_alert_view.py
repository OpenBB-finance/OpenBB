"""Whale Alert view"""
__docformat__ = "numpy"

import logging
import os

from gamestonk_terminal.cryptocurrency.onchain import whale_alert_model
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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

    if df.empty:
        console.print("Error with Whale Alert requests\n")
        return

    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend)

    if not show_address:
        df = df.drop(["from_address", "to_address"], axis=1)
    else:
        df = df.drop(["from", "to", "blockchain"], axis=1)

    for col in ["amount_usd", "amount"]:
        df[col] = df[col].apply(lambda x: lambda_long_number_format(x))

    print_rich_table(
        df.head(top),
        headers=list(df.columns),
        show_index=False,
        title="Large Value Transactions",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "whales",
        df_data,
    )
