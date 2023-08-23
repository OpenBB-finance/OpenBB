"""SDK Helper Functions"""
__docformat__ = "numpy"

from typing import List, Optional, Union

import pandas as pd

from openbb_terminal.futures import yfinance_model
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import databento_model


def get_historical(
    symbols: Union[str, List[str]],
    start_date: str,
    end_date: str,
    source: Optional[str] = "YahooFinance",
    expiry: Optional[str] = "",
) -> pd.DataFrame:
    """Get historical futures data

    Parameters
    ----------
    symbols : Union[str, List[str]]
        The futures symbols you want to retrieve historical data for.
        It can be either a single symbol as a string or a list of symbols.
    start_date : str
        The start date of the historical data you want to retrieve. The date should be in the format "YYYY-MM-DD".
    end_date : str
        The end date of the historical data you want to retrieve. The date should be in the format "YYYY-MM-DD".
    source : Optional[str], default "YahooFinance"
        The source from which you want to retrieve the historical data.
        Valid values for the source are "YahooFinance" and "DataBento".
    expiry : Optional[str], default ""
        The expiry date for futures contracts. This parameter is optional and defaults to an empty string.
        It is applicable only when the source is "YahooFinance" and the symbols are futures contracts.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the historical data for the given symbols and date range.
    """
    if source == "YahooFinance":
        if isinstance(symbols, str):
            symbols = [symbols]
        return yfinance_model.get_historical_futures(
            symbols, expiry, start_date, end_date
        )
    if source == "DataBento":
        if isinstance(symbols, list):
            console.print(
                "DataBento only supports one symbol at a time.  Using first symbol."
            )
            symbols = symbols[0]
        return databento_model.get_historical_futures(symbols, start_date, end_date)
    return pd.DataFrame()
