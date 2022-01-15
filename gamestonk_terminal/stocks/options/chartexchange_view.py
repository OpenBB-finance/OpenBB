"""Chartexchange view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.stocks.options import chartexchange_model
from gamestonk_terminal.rich_config import console


def display_raw(
    ticker: str, date: str, call: bool, price: str, num: int = 20, export: str = ""
) -> None:
    """Return raw stock data[chartexchange]

    Parameters
    ----------
    ticker : str
        Ticker for the given option
    date : str
        Date of expiration for the option
    call : bool
        Whether the underlying asset should be a call or a put
    price : float
        The strike of the expiration
    num : int
        Number of rows to show
    export : str
        Export data as CSV, JSON, XLSX
    """

    df = chartexchange_model.get_option_history(ticker, date, call, price)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hist",
        df,
    )

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df.head(num),
                headers=df.columns,
                tablefmt="fancy_grid",
                showindex=True,
                floatfmt=".2f",
            )
        )
    else:
        console.print(df.to_string(index=False))

    console.print("")
