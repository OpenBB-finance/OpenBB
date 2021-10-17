"""Yfinance view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.stocks.technical_analysis.yfinance_model import get_history
import gamestonk_terminal.feature_flags as gtff


def get_raw(
    ticker: str, period: str, interval: str, export: str, sort: str, des: bool
) -> None:
    """Return raw stock data [Source: Yahoo Finance]

    Parameters
    ----------
    ticker : str
        Ticker to display data for
    period : str
        Period to show information for
    interval : str
        Format of export file
    export : str
        Export data as CSV, JSON, XLSX
    sort : str
        The column to sort by
    des : bool
        Whether to sort descending
    """

    history = get_history(ticker, period, interval)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "history",
        history,
    )

    history = history.sort_values(by=sort, ascending=des)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                history,
                headers=[x.title() if x != "" else "Date" for x in history.columns],
                tablefmt="fancy_grid",
                showindex=True,
                floatfmt=".2f",
            )
        )
    else:
        print(history.to_string(index=False))

    print("")
