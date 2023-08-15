from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta

from openbb_yfinance.utils.futures_reference import MONTHS, futures_data


def get_futures_curve(symbol: str, date: Optional[str]) -> pd.DataFrame:
    """Helper to get the futures curve

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
    exchange = futures_data[futures_data["Ticker"] == symbol]["Exchange"].values[0]
    today = datetime.today()
    futures_index = list()
    futures_curve = list()
    historical_curve = list()
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
