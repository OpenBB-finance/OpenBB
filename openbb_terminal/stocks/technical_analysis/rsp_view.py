""" Relative Strength Percentile View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.technical_analysis import rsp_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_rsp(
    s_ticker: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    tickers_show: bool = False,
):
    """Display Relative Strength Percentile [Source: https://github.com/skyte/relative-strength]

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    export : str
        Format of export file
    tickers_show : bool
        Boolean to check if tickers in the same industry as the stock should be shown
    """

    rsp_stock, rsp_industry, df_stock_p, df_industries_p = rsp_model.get_rsp(s_ticker)
    if rsp_stock.empty or rsp_industry.empty:
        console.print(f"[red]Ticker '{s_ticker}' not found.\n[/red]")
    else:
        tickers = pd.DataFrame(rsp_industry["Tickers"])
        del rsp_industry["Tickers"]
        print_rich_table(
            rsp_stock,
            headers=list(rsp_stock.columns),
            show_index=False,
            title="Relative Strength Percentile of Stock (relative to SPY)",
            export=bool(export),
        )
        print_rich_table(
            rsp_industry,
            headers=list(rsp_industry.columns),
            show_index=False,
            title="Relative Strength Percentile of Industry the ticker is part of",
            export=bool(export),
        )
        if tickers_show:
            print_rich_table(
                tickers,
                headers=list(tickers.columns),
                show_index=False,
                title="Tickers in same industry as chosen stock",
            )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
            "rsp_stock",
            df_stock_p,
            sheet_name,
        )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
            "rsp_industry",
            df_industries_p,
            sheet_name,
        )
