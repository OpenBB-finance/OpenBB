import logging

import pandas as pd
import pandas_market_calendars as mcal

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_all_holiday_exchange_short_names() -> pd.DataFrame:
    """Get all holiday exchanges short names.

    Returns
    -------
    pd.DataFrame
        All available exchanges with holiday data (short names)
    """
    exchange_short_names = mcal.calendar_registry.get_calendar_names()

    df = pd.DataFrame(exchange_short_names, columns=["short_name"])

    return df


@log_start_end(log=logger)
def get_exchange_holidays(exchange_symbol: str, year: int) -> pd.DataFrame:
    """Get all short name of each exchange that we hold holiday calendar for.

    Parameters
    ----------
    symbol : str
        Exchange symbol
    year : int
        Calendar year

    Returns
    -------
    pd.DataFrame
        All available exchanges with holiday data (short names)
    """

    cal = mcal.get_calendar(exchange_symbol)
    holidays = pd.DataFrame(cal.holidays().holidays)

    start_date = str(year) + "-01-01"
    end_date = str(year) + "-12-31"
    holidays.columns = ["Holiday Date"]

    mask = (holidays["Holiday Date"] >= start_date) & (
        holidays["Holiday Date"] <= end_date
    )
    exchange_holidays = holidays.loc[mask].copy()

    exchange_holidays["Holiday Date"] = exchange_holidays["Holiday Date"].astype(str)

    return exchange_holidays
