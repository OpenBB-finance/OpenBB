"""Finviz Comparison Model"""

__docformat__ = "numpy"

import logging
from typing import List

import pandas as pd
from finvizfinance.screener import (
    financial,
    overview,
    ownership,
    performance,
    technical,
    valuation,
)

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_comparison_data(similar: List[str], data_type: str = "overview"):
    """Screener Overview.

    Parameters
    ----------
    similar:
        List of similar companies.
        Comparable companies can be accessed through
        finnhub_peers(), finviz_peers(), polygon_peers().
    data_type : str
        Data type between: overview, valuation, financial, ownership, performance, technical

    Returns
    -------
    pd.DataFrame
        Dataframe with overview, valuation, financial, ownership, performance or technical
    """
    if data_type == "overview":
        screen = overview.Overview()
    elif data_type == "valuation":
        screen = valuation.Valuation()
    elif data_type == "financial":
        screen = financial.Financial()
    elif data_type == "ownership":
        screen = ownership.Ownership()
    elif data_type == "performance":
        screen = performance.Performance()

    elif data_type == "technical":
        screen = technical.Technical()
    else:
        console.print("Invalid selected screener type")
        return pd.DataFrame()

    screen.set_filter(ticker=",".join(similar))
    try:
        screen_df = screen.screener_view(verbose=0)
        screen_df.columns = screen_df.columns.str.strip()
        screen_df = screen_df.rename(
            columns={
                "Perf Week": "1W",
                "Perf Month": "1M",
                "Perf Quart": "3M",
                "Perf Half": "6M",
                "Perf Year": "1Y",
                "Perf YTD": "YTD",
                "Volatility W": "1W Volatility",
                "Volatility M": "1M Volatility",
            }
        )
        return screen_df
    except IndexError:
        console.print("[red]Invalid data from website[red]\n")
        return pd.DataFrame()
    except AttributeError:
        console.print("[red]Invalid data from website[red]\n")
        return pd.DataFrame()
