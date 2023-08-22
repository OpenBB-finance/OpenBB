"""yfinance helpers module."""


from datetime import (
    date as dateType,
    datetime,
)
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta

from openbb_yfinance.utils.references import MONTHS


def get_futures_data() -> pd.DataFrame:
    """Return the dataframe of the futures csv file"""
    return pd.read_csv(Path(__file__).resolve().parent / "futures.csv")


def get_futures_curve(symbol: str, date: Optional[dateType]) -> pd.DataFrame:
    """Get the futures curve for a given symbol.

    Parameters
    ----------
    symbol: str
        Symbol to get futures for
    date: Optional[str]
        Optional historical date to get curve for

    Returns
    -------
    pd.DataFrame
        DataFrame with futures curve
    """
    futures_data = get_futures_data()
    exchange = futures_data[futures_data["Ticker"] == symbol]["Exchange"].values[0]
    today = datetime.today()
    futures_index = []
    futures_curve = []
    historical_curve = []
    i = 0
    empty_count = 0
    # Loop through until we find 12 consecutive empty months
    while empty_count < 12:
        future = today + relativedelta(months=i)
        future_symbol = (
            f"{symbol}{MONTHS[future.month]}{str(future.year)[-2:]}.{exchange}"
        )
        data = yf.download(future_symbol, progress=False, ignore_tz=True)

        if data.empty:
            empty_count += 1

        else:
            empty_count = 0
            futures_index.append(future.strftime("%b-%Y"))
            futures_curve.append(data["Adj Close"].values[-1])
            if date is not None:
                historical_curve.append(
                    data["Adj Close"].get(date.strftime("%Y-%m-%d"), None)
                )

        i += 1

    if not futures_index:
        return pd.DataFrame({"date": [], "Last Price": []})

    if historical_curve:
        print(historical_curve)
        return pd.DataFrame(
            {"Last Price": historical_curve, "expiration": futures_index}
        )
    return pd.DataFrame({"Last Price": futures_curve, "expiration": futures_index})
