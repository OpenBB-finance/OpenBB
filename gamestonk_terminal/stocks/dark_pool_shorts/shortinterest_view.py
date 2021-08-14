""" Short Interest View """
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data

from gamestonk_terminal.stocks.dark_pool_shorts import shortinterest_model


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
