"""StockAnalysis.com view functions"""
__docformat__ = "numpy"

import logging
import os
from typing import List

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.etf import stockanalysis_model
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_overview(symbol: str, export: str = ""):
    """Print etf overview information

    Parameters
    ----------
    symbol:str
        ETF symbols to display overview for
    export:str
        Format to export data
    """

    if symbol.upper() not in stockanalysis_model.get_all_names_symbols()[0]:
        console.print(f"{symbol.upper()} not found in ETFs\n")
        return

    data = stockanalysis_model.get_etf_overview(symbol)

    print_rich_table(
        data,
        headers=list(data.columns),
        title="ETF Overview Information",
        show_index=True,
    )
    console.print("")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "overview", data)


@log_start_end(log=logger)
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
    print_rich_table(
        data[:num_to_show],
        headers=list(data.columns),
        title="ETF Holdings",
        show_index=True,
    )
    console.print("")

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "holdings", data)


@log_start_end(log=logger)
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
            console.print(f"{etf} not a known symbol.\n")
            etf_list.remove(etf)

    data = stockanalysis_model.compare_etfs(symbols)
    if data.empty:
        console.print("No data found for given ETFs\n")
        return
    print_rich_table(data, headers=list(data.columns), title="ETF Comparisons")
    console.print("")
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "overview", data)


@log_start_end(log=logger)
def display_etf_by_name(name: str, limit: int, export: str):
    """Display ETFs matching search string. [Source: StockAnalysis]

    Parameters
    ----------
    name: str
        String being matched
    limit: int
        Limit of ETFs to display
    export: str
        Export to given file type

    """
    matching_etfs = stockanalysis_model.get_etfs_by_name(name)

    print_rich_table(
        matching_etfs.head(limit),
        show_index=False,
        title="ETF Search Result",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ln_sa",
        matching_etfs,
    )
