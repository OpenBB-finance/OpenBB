""" Short Interest View """
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data

from gamestonk_terminal.stocks.discovery import shortinterest_model


def high_short_interest(num: int, export: str):
    """Prints top N high shorted interest stocks from https://www.highshortinterest.com

    Parameters
    ----------
    num: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_high_short_interest = shortinterest_model.get_high_short_interest()
    df_high_short_interest = df_high_short_interest.iloc[1:].head(n=num)

    print(
        tabulate(
            df_high_short_interest,
            headers=df_high_short_interest.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lowfloat",
        df_high_short_interest,
    )


def low_float(num: int, export: str):
    """Prints top N low float stocks from https://www.lowfloat.com

    Parameters
    ----------
    num: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_low_float = shortinterest_model.get_low_float()
    df_low_float = df_low_float.iloc[1:].head(n=num)

    print(
        tabulate(
            df_low_float,
            headers=df_low_float.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lowfloat",
        df_low_float,
    )


# TODO: Add https://www.pennystockflow.com
