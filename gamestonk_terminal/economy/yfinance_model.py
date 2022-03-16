""" Yahoo Finance Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import yfinance as yf

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

INDICES = {
    "sp500": {"name": "S&P 500", "ticker": "^GSPC"},
    "nasdaq": {"name": "Nasdaq Composite", "ticker": "^IXIC"},
    "dowjones": {"name": "Dow Jones Industrial Average", "ticker": "^DJI"},
    "vix": {"name": "CBOE Volatility Index", "ticker": "^VIX"},
    "russel": {"name": "Russel 2000 Index", "ticker": "^RUT"},
    "tsx": {"name": "TSX Composite", "ticker": "^GSPTSE"},
    "nikkei": {"name": "Nikkei 255 Stock Average", "ticker": "^N225"},
    "shanghai": {"name": "Shanghai Composite Index", "ticker": "000001.SS"},
    "ftse100": {"name": "FTSE 100 Index ('footsie')", "ticker": "^FTSE"},
    "stoxx50": {"name": "Euro STOXX 50", "ticker": "^STOXX50E"},
    "dax": {"name": "DAX Performance Index", "ticker": "^GDAXI"},
    "cac40": {"name": "CAC 40 Index", "ticker": "^FCHI"},
}


@log_start_end(log=logger)
def get_index(
    index: str,
    interval: str = "1d",
    start_date: int = None,
    end_date: int = None,
    column: str = "Adj Close",
) -> pd.Series:
    """Obtain data on any index [Source: Yahoo Finance]

    Parameters
    ----------
    index: str
        The index you wish to collect data for.
    start_date : str
       the selected country
    end_date : bool
        The currency you wish to convert the data to.
    interval : str
        Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo or 3mo
        Intraday data cannot extend last 60 days
    column : str
        The column you wish to select, by default this is Adjusted Close.

    Returns
    ----------
    pd.Series
        A series with the requested index
    """
    if index.lower() in INDICES:
        ticker = INDICES[index.lower()]["ticker"]
    else:
        ticker = index

    index_data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval=interval,
        progress=False,
        show_errors=False,
    )

    if column not in index_data.columns:
        console.print(
            f"The chosen column is not available for {ticker}. Please choose "
            f"between: {', '.join(index_data.columns)}\n"
        )
        return pd.Series()
    if index_data.empty or len(index_data) < 2:
        console.print(
            f"The chosen index {ticker}, returns no data. Please check if "
            f"there is any data available.\n"
        )
        return pd.Series()

    return index_data[column]
