"""Finviz Comparison View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.comparison_analysis import finviz_compare_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def screener(
    similar: List[str],
    data_type: str = "overview",
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Screener.

    Parameters
    ----------
    similar : List[str]
        Similar companies to compare income with.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    data_type : str
        Screener to use.  One of {overview, valuation, financial, ownership, performance, technical}
    export : str
        Format to export data
    """
    df_screen = finviz_compare_model.get_comparison_data(
        similar=similar, data_type=data_type
    )

    if df_screen is None or df_screen.empty:
        console.print("No screened data found.")
    else:
        print_rich_table(
            df_screen,
            headers=list(df_screen.columns),
            show_index=False,
            title="Stock Screener",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        data_type,
        df_screen,
        sheet_name,
    )
