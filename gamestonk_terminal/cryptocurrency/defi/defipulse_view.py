"""DeFi Pulse view"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.cryptocurrency.defi import defipulse_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff


def display_defipulse(top: int, sortby: str, descend: bool, export: str = "") -> None:
    """Displays all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Parameters
    ----------
    top: int
        Number of records to display
    sortby: str
        Key by which to sort data
    descend: bool
        Flag to sort data descending
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = defipulse_model.get_defipulse_index()
    df_data = df.copy()

    df = df.sort_values(by=sortby, ascending=descend)

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
        "dpi",
        df_data,
    )
