"""StockAnalysis.com view functions"""
__docformat__ = "numpy"

import os
from typing import List

import pandas as pd
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

    if symbol.upper() not in stockanalysis_model.get_all_names_symbols()[0]:
        print(f"{symbol.upper()} not found in ETFs\n")
        return

    data = stockanalysis_model.get_etf_overview(symbol)

    print(tabulate(data, headers=data.columns, tablefmt="fancy_grid"), "\n")

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
        ),
        "\n",
    )
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

    etf_list = stockanalysis_model.get_all_names_symbols()[0]
    for etf in symbols:
        if etf not in etf_list:
            print(f"{etf} not a known symbol. ")
            etf_list.remove(etf)

    data = stockanalysis_model.compare_etfs(symbols)
    print(tabulate(data, headers=data.columns, tablefmt="fancy_grid"), "\n")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "overview", data)


def view_search(to_match: str, export: str):
    """Display ETFs matching search string

    Parameters
    ----------
    to_match: str
        String being matched
    export: str
        Export to given file type

    """
    matching_etfs = stockanalysis_model.search_etfs(to_match)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "search",
        pd.DataFrame(data=matching_etfs),
    )
    print(*matching_etfs, sep="\n")
    if len(matching_etfs) == 0:
        print("No matches found")
    print("")
