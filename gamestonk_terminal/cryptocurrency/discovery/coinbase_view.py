"""Coinbase view"""
__docformat__ = "numpy"

import os
from typing import Optional
from tabulate import tabulate
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.cryptocurrency.discovery import coinbase_model
from gamestonk_terminal.helper_funcs import long_number_format
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import plot_order_book

register_matplotlib_converters()


def display_trading_pairs(export: str) -> None:
    """Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_trading_pairs()
    df_data = df.copy()

    for col in [
        "base_min_size",
        "base_max_size",
        "min_market_funds",
        "max_market_funds",
    ]:
        df[col] = df[col].apply(lambda x: long_number_format(x))

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
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
        "pairs",
        df_data,
    )


def display_order_book(product_id: str) -> None:
    """Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH

    """

    bids, asks, pair = coinbase_model.get_order_book(product_id)
    plot_order_book(bids, asks, pair)


def display_trades(
    product_id: str, limit: int = 1000, side: Optional[str] = None, export: str = ""
) -> None:
    """Display last N trades for chosen trading pair. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    limit: int
        Last <limit> of trades. Maximum is 1000.
    side: Optional[str]
        You can chose either sell or buy side. If side is not set then all trades will be displayed.
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_trades(product_id, limit, side)
    df_data = df.copy()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
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
        "trades",
        df_data,
    )


def display_candles(product_id: str, interval: str, export):
    """Get candles for chosen trading pair and time interval. [Source: Coinbase]

    Parameters
    ----------
    product_id: str
        Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH
    interval: str
        Time interval. One from 1m, 5m ,15m, 1h, 6h, 24h
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_candles(product_id, interval)
    df_data = df.copy()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=True,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pairs",
        df_data,
    )


def display_currencies(export: str):
    df = coinbase_model.get_all_currencies()
    df_data = df.copy()

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
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
        "pairs",
        df_data,
    )
