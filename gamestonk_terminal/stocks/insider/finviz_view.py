""" Finviz View """
__docformat__ = "numpy"

import os
import pandas as pd
from tabulate import tabulate
from gamestonk_terminal.stocks.insider import finviz_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff


def last_insider_activity(ticker: str, num: int, export: str):
    """Display insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    ticker : str
        Stock ticker
    num : int
        Number of latest insider activity to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    d_finviz_insider = finviz_model.get_last_insider_activity(ticker)
    df = pd.DataFrame.from_dict(d_finviz_insider)
    df.set_index("Date", inplace=True)
    df = df[
        [
            "Relationship",
            "Transaction",
            "#Shares",
            "Cost",
            "Value ($)",
            "#Shares Total",
            "Insider Trading",
            "SEC Form 4",
        ]
    ]

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(num),
                tablefmt="fancy_grid",
                floatfmt=".2f",
                headers=list(df.columns),
                showindex=True,
            )
        )
    else:
        print(df.to_string())
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lins",
        df,
    )
