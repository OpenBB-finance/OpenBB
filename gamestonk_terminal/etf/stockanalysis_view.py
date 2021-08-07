"""StockAnalysis.com view functions"""
__docformat__ = "numpy"

from typing import List
import os

from tabulate import tabulate

from gamestonk_terminal.etf import stockanalysis_model
from gamestonk_terminal.helper_funcs import export_data


def view_overview(symbol: str, export: str):
    """Print etf overview information

    Parameters
    ----------
    symbol:str
        ETF symbols to display overview for
    export:str
        Format to export data
    """

    data = stockanalysis_model.get_etf_overview(symbol)

    print(tabulate(data, headers=data.columns, tablefmt="fancy_grid"))
    print("")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "overview", data)


def view_holdings(symbol: str, num_to_show: int, export: str):
    """

    Parameters
    ----------
    symbol: str
        ETF symbol to show holdings for
    num_to_show: int
        Number of holdings to show
    export: str
        Format to export data
    """

    data = stockanalysis_model.get_etf_holdings(symbol)
    print(
        tabulate(
            data[:num_to_show],
            headers=data.columns,
            tablefmt="fancy_grid",
        )
    )
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "holdings", data)


def view_comparisons(symbols: List[str], export: str):
    """Show ETF comparisons

    Parameters
    ----------
    symbols: List[str]
        List of ETF symbols
    export: str
        Format to export data
    """
    data = stockanalysis_model.compare_etfs(symbols)
    print(tabulate(data, headers=data.columns, tablefmt="fancy_grid"))
    print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "overview", data)
