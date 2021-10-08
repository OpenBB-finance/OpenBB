"""ARK View"""
__docformat__ = "numpy"

import os

import pandas as pd
from tabulate import tabulate

from gamestonk_terminal.stocks.due_diligence import ark_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data


def display_ark_trades(
    ticker: str, num: int = 20, export: str = "", show_ticker: bool = False
):
    """Display ARK trades for ticker

    Parameters
    ----------
    ticker : str
        Ticker to get trades for
    num: int
        Number of rows to show
    export : str, optional
        Format to export data
    show_ticker: bool
        Flag to show ticker in table
    """
    ark_holdings = ark_model.get_ark_trades_by_ticker(ticker)

    if ark_holdings.empty:
        print("Issue getting data from cathiesark.com.  Likely no trades found.\n")
        return

    # Since this is for a given ticker, no need to show it
    if not show_ticker:
        ark_holdings = ark_holdings.drop(columns=["ticker"])
    ark_holdings["Total"] = ark_holdings["Total"] / 1_000_000
    ark_holdings.rename(
        columns={"Close": "Close ($)", "Total": "Total ($1M)"}, inplace=True
    )

    ark_holdings.index = pd.Series(ark_holdings.index).apply(
        lambda x: x.strftime("%Y-%m-%d")
    )
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                ark_holdings.head(num),
                headers=ark_holdings.columns,
                showindex=True,
                floatfmt=("", ".4f", ".4f", ".4f", "", ".2f", ".2f", ".3f"),
                tablefmt="fancy_grid",
            )
        )
    else:
        print(ark_holdings.head(num).to_string())
    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "arktrades", ark_holdings
    )
