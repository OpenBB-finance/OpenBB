"""ARK View"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal.stocks.due_diligence import ark_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data


def display_ark_trades(ticker: str, num: int = 20, export: str = ""):
    """Display ARK trades for ticker

    Parameters
    ----------
    ticker : str
        Ticker to get trades for
    num: int
        Number of rows to show
    export : str, optional
        Format to export data
    """
    ark_holdings = ark_model.get_ark_trades_by_ticker(ticker)
    # Since this is for a given ticker, no need to show it
    ark_holdings = ark_holdings.drop(columns=["ticker"])

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                ark_holdings.head(num),
                headers=ark_holdings.columns,
                showindex=False,
                floatfmt=".4f",
                tablefmt="fancy_grid",
            )
        )
    else:
        print(ark_holdings.head(num).to_string())
    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "arktrades", ark_holdings
    )
