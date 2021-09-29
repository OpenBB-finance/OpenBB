"""Llama View"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.discovery import llama_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff


def display_defi_protocols(
    top: int, sortby: str, descend: bool, description: bool, export: str = ""
) -> None:
    """Display information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    description: bool
        Flag to display description of protocol
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = llama_model.get_defi_protocols()
    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend)

    if not description:
        df.drop(["description", "url"], axis=1, inplace=True)
    else:
        df = df[
            [
                "name",
                "symbol",
                "category",
                "description",
                "url",
            ]
        ]

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(top),
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
        "protocols",
        df_data,
    )
