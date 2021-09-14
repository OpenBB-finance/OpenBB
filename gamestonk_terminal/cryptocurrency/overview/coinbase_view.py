"""Coinbase view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.cryptocurrency.overview import coinbase_model
from gamestonk_terminal.helper_funcs import long_number_format


def display_trading_pairs(top: int, sortby: str, descend: bool, export: str) -> None:
    """Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    top: int
        Top n of pairs
    sortby: str
        Key to sortby data
    descend: bool
        Sort descending flag
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

    df = df.sort_values(by=sortby, ascending=descend).head(top)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
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
