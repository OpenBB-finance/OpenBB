""" Market Watch View """
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.due_diligence import marketwatch_model
from gamestonk_terminal.rich_config import console

# pylint: disable=too-many-branches


def sec_filings(ticker: str, num: int, export: str):
    """Display SEC filings for a given stock ticker. [Source: Market Watch]

    Parameters
    ----------
    ticker : str
        Stock ticker
    num : int
        Number of ratings to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_financials = marketwatch_model.get_sec_filings(ticker)
    print(
        tabulate(
            df_financials.head(num),
            headers=df_financials.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        )
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sec",
        df_financials,
    )
