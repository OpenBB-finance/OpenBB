"""SDK Helper Functions"""
__docformat__ = "numpy"

from typing import List, Optional, Union

import pandas as pd

from openbb_terminal.futures import yfinance_model
from openbb_terminal.stocks import databento_model


def get_historical(
    symbols: Union[str, List[str]],
    start_date: str,
    end_date: str,
    source: Optional[str] = "YahooFinance",
    expiry: Optional[str] = "",
) -> pd.DataFrame:
    """Get historical futures data"""
    if source == "YahooFinance":
        if isinstance(symbols, str):
            symbols = [symbols]
        return yfinance_model.get_historical_futures(
            symbols, expiry, start_date, end_date
        )
    if source == "DataBento":
        if isinstance(symbols, list):
            print("DataBento only supports one symbol at a time.  Using first symbol.")
            symbols = symbols[0]
        return databento_model.get_historical_futures(symbols, start_date, end_date)
    return pd.DataFrame()
