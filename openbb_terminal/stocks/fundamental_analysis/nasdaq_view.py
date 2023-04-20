"""Nasdaq View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import nasdaq_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def sec_filings(
    symbol: str,
    limit: int = 5,
    export: str = "",
    sheet_name: Optional[str] = None,
    year: Optional[int] = None,
    form_group: Optional[str] = None,
):
    """Display SEC filings for a given stock ticker. [Source: Nasdaq]

    Parameters
    ----------
    symbol: str
        Stock ticker symbol
    limit: int
        Number of ratings to display
    export: str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    year: Optional[int]
        The year to grab from. The year will be ignored if form_group is not specified
    form_group: Optional[str]
        The form type to filter for:
        Choose from: annual, quarterly, proxies, insiders, 8-K, registrations, comments
    """
    df_financials = nasdaq_model.get_sec_filings(
        symbol.upper().replace("-", "."), limit, year, form_group
    )
    if not isinstance(df_financials, pd.DataFrame) or df_financials.empty:
        console.print(f"No data found for {symbol}")
        return
    print_rich_table(
        df_financials,
        headers=list(df_financials.columns),
        show_index=True,
        title="SEC Filings",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "sec",
        df_financials,
        sheet_name,
    )
