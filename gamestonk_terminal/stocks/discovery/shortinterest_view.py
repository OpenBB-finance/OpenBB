""" Short Interest View """
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data

from gamestonk_terminal.stocks.discovery import shortinterest_model


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


def hot_penny_stocks(num: int, export: str):
    """Prints top N hot penny stocks from https://www.pennystockflow.com

    Parameters
    ----------
    num: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_penny_stocks = shortinterest_model.get_today_hot_penny_stocks()

    print(
        tabulate(
            df_penny_stocks.head(num),
            headers=df_penny_stocks.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        ),
        "\n",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hotpenny",
        df_penny_stocks,
    )
