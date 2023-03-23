"""StockAnalysis.com view functions"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import stockanalysis_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_overview(symbol: str, export: str = "", sheet_name: Optional[str] = None):
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
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "overview",
        data,
        sheet_name,
    )


@log_start_end(log=logger)
def view_holdings(
    symbol: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """

    Parameters
    ----------
    symbol: str
        ETF symbol to show holdings for
    limit: int
        Number of holdings to show
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """

    data = stockanalysis_model.get_etf_holdings(symbol)
    print_rich_table(
        data,
        headers=list(data.columns),
        title="ETF Holdings",
        show_index=True,
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "holdings",
        data,
        sheet_name,
    )


@log_start_end(log=logger)
def view_comparisons(
    symbols: List[str], export: str = "", sheet_name: Optional[str] = None
):
    """Show ETF comparisons

    Parameters
    ----------
    symbols: List[str]
        List of ETF symbols
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    """

    etf_list = stockanalysis_model.get_all_names_symbols()[0]
    for etf in symbols:
        if etf not in etf_list:
            console.print(f"{etf} not a known symbol.\n")
            symbols.remove(etf)

    data = stockanalysis_model.compare_etfs(symbols)
    if data.empty:
        console.print("No data found for given ETFs\n")
        return
    print_rich_table(
        data,
        headers=list(data.columns),
        title="ETF Comparisons",
        show_index=True,
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "overview",
        data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_etf_by_name(
    name: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """Display ETFs matching search string. [Source: StockAnalysis]

    Parameters
    ----------
    name: str
        String being matched
    limit: int
        Limit of ETFs to display
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export to given file type

    """
    matching_etfs = stockanalysis_model.get_etfs_by_name(name)

    print_rich_table(
        matching_etfs,
        show_index=False,
        title="ETF Search Result",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ln_sa",
        matching_etfs,
        sheet_name,
    )
