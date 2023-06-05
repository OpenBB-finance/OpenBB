""" Yahoo Finance Model """
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_series(
    series_id: str,
    interval: str = "1d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    column: str = "Adj Close",
) -> pd.Series:
    """Obtain data on any index [Source: Yahoo Finance]

    Parameters
    ----------
    series_id: str
        The series you wish to collect data for.
    start_date : Optional[str]
        the selected country
    end_date : Optional[str]
        The currency you wish to convert the data to.
    interval : str
        Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo or 3mo
        Intraday data cannot extend last 60 days
    column : str
        The column you wish to select, by default this is Adjusted Close.

    Returns
    -------
    pd.Series
        A series with the requested index
    """
    try:
        if start_date:
            datetime.strptime(str(start_date), "%Y-%m-%d")
        if end_date:
            datetime.strptime(str(end_date), "%Y-%m-%d")
    except ValueError:
        console.print("[red]Please format date as YYYY-MM-DD[/red]\n")
        return pd.Series(dtype="object")

    index_data = yf.download(
        series_id,
        start=start_date,
        end=end_date,
        interval=interval,
        progress=False,
        show_errors=False,
    )

    if column not in index_data.columns:
        console.print(
            f"The chosen column is not available for {series_id}. Please choose "
            f"between: {', '.join(index_data.columns)}\n"
        )
        return pd.Series(dtype="float64")
    if index_data.empty or len(index_data) < 2:
        console.print(
            f"The chosen index {series_id}, returns no data. Please check if "
            f"there is any data available.\n"
        )
        return pd.Series(dtype="float64")

    return index_data[column]
