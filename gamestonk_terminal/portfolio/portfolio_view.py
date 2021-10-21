"""Portfolio View"""
__docformat__ = "numpy"

import os

import pandas as pd
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff


def get_load():
    """
    Prints instructions to load a CSV

    Returns
    ----------
    text : str
        Returns instructions for loading data
    """
    text = """
In order to load a CSV do the following:

1. Add headers to the first row, below is data for each column:\n
\t1. Identifier for the asset (such as a stock ticker)
\t2. Type of asset (stock, bond, option, crypto)
\t3. The volume of the asset transacted
\t4. The buy date in yyyy/mm/dd hh:mm format (hh:mm excludable, but reduces accuracy)
\t5. The Price paid for the asset
\t6. Any fees paid during the transaction
\t7. A premium paid or received if this was an option
\t8. Whether the asset was bought (covered) or sold (shorted)\n
2. Place this file in gamestonk_terminal/portfolio/portfolios\n
        """
    print(text)


def save_df(df: pd.DataFrame, name: str):
    """
    Saves the portfolio as a csv

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be saved
    name : str
        The name of the string
    """
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(path, "portfolios", f"{name}.csv"))
    df.to_csv(path, index=False)


def show_df(df: pd.DataFrame, show: bool):
    """
    Shows the given dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be shown
    show : bool
        Whether to show the dataframe index
    """

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=show,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")
