"""Yahoo Finance helpers module."""

from datetime import (
    date as dateType,
    datetime,
)
from pathlib import Path
from typing import Any, Literal, Optional, Union

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta
from openbb_yfinance.utils.references import MONTHS


def get_futures_data() -> pd.DataFrame:
    """Return the dataframe of the futures csv file."""
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
    try:
        exchange = futures_data[futures_data["Ticker"] == symbol]["Exchange"].values[0]
    except IndexError:
        return pd.DataFrame({"Last Price": [], "expiration": []})

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
        return pd.DataFrame(
            {"Last Price": historical_curve, "expiration": futures_index}
        )
    return pd.DataFrame({"Last Price": futures_curve, "expiration": futures_index})


# pylint: disable=too-many-arguments,unused-argument
def yf_download(
    symbol: str,
    start_date: Optional[Union[str, dateType]] = None,
    end_date: Optional[Union[str, dateType]] = None,
    interval: str = "1d",
    period: str = "max",
    prepost: bool = False,
    actions: bool = False,
    progress: bool = False,
    ignore_tz: bool = True,
    keepna: bool = False,
    repair: bool = False,
    rounding: bool = False,
    group_by: Literal["symbol", "column"] = "column",
    adjusted: bool = False,
    **kwargs: Any,
) -> pd.DataFrame:
    """Get yFinance OHLC data for any ticker and interval available."""
    symbol = symbol.upper()
    _start_date = start_date

    if interval in ["60m", "1h"]:
        period = "2y" if period in ["5y", "10y", "max"] else period
        _start_date = None

    if interval in ["2m", "5m", "15m", "30m", "90m"]:
        _start_date = (datetime.now().date() - relativedelta(days=58)).strftime(
            "%Y-%m-%d"
        )

    if interval == "1m":
        period = "5d"
        _start_date = None

    if adjusted is False:
        kwargs = dict(auto_adjust=False, back_adjust=False)

    data = yf.download(
        tickers=symbol,
        start=_start_date,
        end=None,
        interval=interval,
        period=period,
        prepost=prepost,
        actions=actions,
        progress=progress,
        ignore_tz=ignore_tz,
        keepna=keepna,
        repair=repair,
        rounding=rounding,
        group_by=group_by,
        **kwargs,
    )
    if not data.empty:
        data = data.reset_index()
        data = data.rename(columns={"Date": "date", "Datetime": "date"})
        data["date"] = pd.to_datetime(data["date"])
        data = data[data["Open"] > 0]

        if start_date is not None:
            data = data[data["date"] >= pd.to_datetime(start_date)]
            if end_date is not None and pd.to_datetime(end_date) > pd.to_datetime(
                start_date
            ):
                data = data[
                    data["date"] <= (pd.to_datetime(end_date) + relativedelta(days=1))
                ]

        if period not in [
            "max",
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
            "10y",
        ]:
            data["date"] = (
                data["date"].dt.tz_localize(None).dt.strftime("%Y-%m-%d %H:%M:%S")
            )
        if interval not in ["1m", "2m", "5m", "15m", "30m", "90m", "60m", "1h"]:
            data["date"] = data["date"].dt.tz_localize(None).dt.strftime("%Y-%m-%d")

        if adjusted is False:
            data = data.drop(columns=["Adj Close"])

        data.columns = data.columns.str.lower().str.replace(" ", "_").to_list()

    return data
