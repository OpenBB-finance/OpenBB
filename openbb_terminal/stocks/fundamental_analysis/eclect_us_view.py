"""Eclect.us view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import eclect_us_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_analysis(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display analysis of SEC filings based on NLP model. [Source: https://eclect.us]

    Parameters
    ----------
    symbol: str
        Ticker symbol to do SEC filings analysis from
    """

    analysis = eclect_us_model.get_filings_analysis(symbol)

    if not analysis.empty:
        print_rich_table(
            analysis,
            title="SEC filings analysis",
            show_index=False,
            export=bool(export),
        )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "analysis",
            analysis,
            sheet_name,
        )
    else:
        console.print("Filings not found from eclect.us")
