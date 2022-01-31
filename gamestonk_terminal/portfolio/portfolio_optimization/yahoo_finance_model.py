"""YFinance Model"""
__docformat__ = "numpy"

import logging
from typing import List

import pandas as pd
import yfinance as yf

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def process_stocks(list_of_stocks: List[str], period: str = "3mo") -> pd.DataFrame:
    """Get adjusted closing price for each stock in the list

    Parameters
    ----------
    list_of_stocks: List[str]
        List of tickers to get historical data for
    period: str
        Period to get data from yfinance

    Returns
    -------
    stock_closes: DataFrame
        DataFrame containing daily (adjusted) close prices for each stock in list
    """

    stock_prices = yf.download(
        list_of_stocks, period=period, progress=False, group_by="ticker"
    )
    stock_closes = pd.DataFrame(index=stock_prices.index)
    for stock in list_of_stocks:
        stock_closes[stock] = stock_prices[stock]["Adj Close"]
    return stock_closes
