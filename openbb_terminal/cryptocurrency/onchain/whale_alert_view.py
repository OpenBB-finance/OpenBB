"""Whale Alert view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.onchain import whale_alert_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_WHALE_ALERT_KEY"])
def display_whales_transactions(
    min_value: int = 800000,
    limit: int = 100,
    sortby: str = "date",
    ascend: bool = False,
    show_address: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]

    Parameters
    ----------
    min_value: int
        Minimum value of trade to track.
    limit: int
        Limit of transactions. Maximum 100
    sortby: str
        Key to sort by.
    ascend: str
        Sort in ascending order.
    show_address: bool
        Flag to show addresses of transactions.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = whale_alert_model.get_whales_transactions(
        min_value=min_value,
        sortby=sortby,
        ascend=ascend,
    )

    if df.empty:
        console.print("Failed to retrieve data.")
        return

    df_data = df.copy()

    if not show_address:
        df = df.drop(["from_address", "to_address"], axis=1)
    else:
        df = df.drop(["from", "to", "blockchain"], axis=1)

    for col in ["amount_usd", "amount"]:
        df[col] = df[col].apply(lambda x: lambda_long_number_format(x))

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Large Value Transactions",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "whales",
        df_data,
        sheet_name,
    )
