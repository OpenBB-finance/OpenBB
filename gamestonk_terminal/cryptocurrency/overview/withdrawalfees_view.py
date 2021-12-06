"""Withdrawal Fees view"""
import os

from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.overview.withdrawalfees_model import (
    get_crypto_withdrawal_fees,
    get_overall_exchange_withdrawal_fees,
    get_overall_withdrawal_fees,
)
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff


def display_overall_withdrawal_fees(export: str, top: int) -> None:
    """Top coins withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    top: int
        Number of coins to search
    """

    df_fees = get_overall_withdrawal_fees(top)

    if df_fees.empty:
        print("\nError in withdrawal fees request\n")
    else:
        print("\nWithdrawal fees on exchanges:")

        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_fees.head(top),
                    headers=df_fees.columns,
                    floatfmt=".1f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            print(df_fees.to_string(index=False), "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "withdrawal_fees",
            df_fees,
        )


def display_overall_exchange_withdrawal_fees(export: str) -> None:
    """Exchange withdrawal fees
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_fees = get_overall_exchange_withdrawal_fees()

    if df_fees.empty:
        print("\nError in withdrawal fees request\n")
    else:
        print("\nWithdrawal fees per exchange:")

        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_fees,
                    headers=df_fees.columns,
                    floatfmt=".1f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            print(df_fees.to_string(index=False), "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "exchange_withdrawal_fees",
            df_fees,
        )


def display_crypto_withdrawal_fees(export: str, symbol: str) -> None:
    """Coin withdrawal fees per exchange
    [Source: https://withdrawalfees.com/]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    symbol: str
        Coin to check withdrawal fees
    """

    res = get_crypto_withdrawal_fees(symbol)
    stats_string = res[0]
    df_fees = res[1]
    if df_fees.empty:
        print("\nError in withdrawal fees request\n")
    else:
        print(f"\nWithdrawal fees for {symbol}:")

        print(f"\n{stats_string}\n")

        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_fees,
                    headers=df_fees.columns,
                    floatfmt=".1f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            print(df_fees.to_string(index=False), "\n")

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "crypto_withdrawal_fees",
            df_fees,
        )
