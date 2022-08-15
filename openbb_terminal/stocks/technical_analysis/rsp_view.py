""" Relative Strength Percentile View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    print_rich_table,
)
from openbb_terminal.stocks.technical_analysis import rsp_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_rsp(
    s_ticker: str = "",
    export: str = "",
):
    """Display Relative Strength Percentile [Source: https://github.com/skyte/relative-strength]

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    """

    rsp_stock, rsp_industry, df_stock_p, df_industries_p = rsp_model.get_rsp(s_ticker)

    if rsp_stock.empty or rsp_industry.empty:
        print("Ticker not found")
    else:
        print_rich_table(
            rsp_stock,
            headers=list(rsp_stock.columns),
            show_index=False,
            title="Relative Strength Percentile of Stock (relative to SPY)",
        )
        print_rich_table(
            rsp_industry,
            headers=list(df_industries_p.columns),
            show_index=False,
            title="Relative Strength Percentile of Industry the ticker is part of",
        )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
            "rsp_stock",
            df_stock_p,
        )
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
            "rsp_industry",
            df_industries_p,
        )
