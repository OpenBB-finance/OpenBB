"""Substack View"""
__docformat__ = "numpy"


import os
from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.defi import substack_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff


def display_newsletters(top: int = 10, export: str = "") -> None:
    """Display DeFi related substack newsletters.
    [Source: substack.com]

    Parameters
    ----------
    top: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = substack_model.get_newsletters()
    df_data = df.copy()

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
        "newsletter",
        df_data,
    )
