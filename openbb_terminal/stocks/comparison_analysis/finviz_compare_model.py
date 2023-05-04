"""Finviz Comparison Model"""
__docformat__ = "numpy"

import logging
from typing import List, Optional

import pandas as pd
from finvizfinance.screener import (
    financial,
    overview,
    ownership,
    performance,
    technical,
    valuation,
)
from finvizfinance.screener.overview import Overview

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_similar_companies(
    symbol: str, compare_list: Optional[List[str]] = None
) -> List[str]:
    """Get similar companies from Finviz.

    Parameters
    ----------
    symbol : str
        Ticker to find comparisons for
    compare_list : List[str]
        List of fields to compare, ["Sector", "Industry", "Country"]

    Returns
    -------
    List[str]
        List of similar companies
    """
    try:
        compare_list = ["Sector", "Industry"] if compare_list is None else compare_list
        similar = Overview().compare(symbol, compare_list, verbose=0)
        similar.columns = [x.strip() for x in similar.columns]
        return similar.Ticker.to_list()
    except Exception as e:
        logger.exception(str(e))
        console.print(e)
        similar = [""]
    return similar


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
        return screen.screener_view(verbose=0)
    except IndexError:
        console.print("[red]Invalid data from website[red]\n")
        return pd.DataFrame()
    except AttributeError:
        console.print("[red]Invalid data from website[red]\n")
        return pd.DataFrame()
