"""Yahoo Finance model"""
__docformat__ = "numpy"

import os
import logging
from typing import Dict, List

import yfinance as yf
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

FUTURES_DATA = pd.read_csv(os.path.join("openbb_terminal", "futures", "futures.csv"))

@log_start_end(log=logger)
def get_search_futures(
    category: str = "",
    exchange: str = "",
):
    """Display search futures [Source: Yahoo Finance]

    Parameters
    ----------
    category: str
        Select the category where the future exists
    exchange: str
        Select the exchange where the future exists
    """
    if category and exchange:
        df = FUTURES_DATA[
            (FUTURES_DATA["Exchange"] == exchange)
            & (FUTURES_DATA["Category"] == category)
        ]
    elif category:
        df = FUTURES_DATA[
            FUTURES_DATA["Category"] == category
        ]
    elif exchange:
        df = FUTURES_DATA[
            FUTURES_DATA["Exchange"] == exchange
        ]
    else:
        df = FUTURES_DATA
    return df

@log_start_end(log=logger)
def get_historical_futures(tickers: List[str]) -> Dict:
    """Get historical futures [Source: Yahoo Finance]

    Parameters
    ----------
    tickers: List[str]
        List of future timeseries tickers to display

    Returns
    ----------
    Dict
        Dictionary with sector weightings allocation
    """
    df = yf.download(tickers, progress=False, period="max")
    return df
