"""Withdrawal Fees view"""
import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.overview.withdrawalfees_model import (
    get_crypto_withdrawal_fees,
    get_overall_exchange_withdrawal_fees,
    get_overall_withdrawal_fees,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_overall_withdrawal_fees(
    limit: int = 15, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Top coins withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    limit: int
        Number of coins to search
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_fees = get_overall_withdrawal_fees(limit)

    if df_fees.empty:
        console.print("\nError in withdrawal fees request\n")
    else:
        console.print("\nWithdrawal fees on exchanges:")

        print_rich_table(
            df_fees,
            headers=list(df_fees.columns),
            show_index=False,
            title="Top Withdrawal Fees",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "withdrawal_fees",
            df_fees,
            sheet_name,
        )


@log_start_end(log=logger)
def display_overall_exchange_withdrawal_fees(
    export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Exchange withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_fees = get_overall_exchange_withdrawal_fees()

    if df_fees.empty:
        console.print("\nError in withdrawal fees request\n")
    else:
        console.print("\nWithdrawal fees per exchange:")

        print_rich_table(
            df_fees,
            headers=list(df_fees.columns),
            show_index=False,
            title="Withdrawal Fees",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "exchange_withdrawal_fees",
            df_fees,
            sheet_name,
        )


@log_start_end(log=logger)
def display_crypto_withdrawal_fees(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    symbol: str
        Coin to check withdrawal fees
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    res = get_crypto_withdrawal_fees(symbol)
    stats_string = res[0]
    df_fees = res[1]
    if df_fees.empty:
        console.print("\nError in withdrawal fees request\n")
    else:
        console.print(f"\nWithdrawal fees for {symbol}:")

        console.print(f"\n{stats_string}\n")

        print_rich_table(
            df_fees,
            headers=list(df_fees.columns),
            show_index=False,
            title="Withdrawal Fees per Exchange",
            export=bool(export),
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "crypto_withdrawal_fees",
            df_fees,
            sheet_name,
        )
