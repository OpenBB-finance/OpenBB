"""Yahoo Finance helpers module."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal, Optional, Union

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.references import INTERVALS, MONTHS, PERIODS
from pandas import DataFrame


def get_futures_data() -> DataFrame:
    """Return the dataframe of the futures csv file."""
    # pylint: disable=import-outside-toplevel
    from pathlib import Path  # noqa
    from pandas import read_csv  # noqa

    return read_csv(Path(__file__).resolve().parent / "futures.csv")


def get_futures_curve(symbol: str, date: Optional[dateType]) -> DataFrame:
    """Get the futures curve for a given symbol.

    Parameters
    ----------
    symbol: str
        Symbol to get futures for
    date: Optional[str]
        Optional historical date to get curve for

    Returns
    -------
    DataFrame
        DataFrame with futures curve
    """
    # pylint: disable=import-outside-toplevel
    import yfinance as yf
    from dateutil.relativedelta import relativedelta

    futures_data = get_futures_data()
    try:
        exchange = futures_data[futures_data["Ticker"] == symbol]["Exchange"].values[0]
    except IndexError:
        return DataFrame({"Last Price": [], "expiration": []})

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
        data = yf.download(future_symbol, progress=False, ignore_tz=True, threads=False)

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
        return DataFrame({"date": [], "Last Price": []})

    if historical_curve:
        return DataFrame({"Last Price": historical_curve, "expiration": futures_index})
    return DataFrame({"Last Price": futures_curve, "expiration": futures_index})


# pylint: disable=too-many-arguments,unused-argument
def yf_download(
    symbol: str,
    start_date: Optional[Union[str, dateType]] = None,
    end_date: Optional[Union[str, dateType]] = None,
    interval: INTERVALS = "1d",
    period: PERIODS = "max",
    prepost: bool = False,
    actions: bool = False,
    progress: bool = False,
    ignore_tz: bool = True,
    keepna: bool = False,
    repair: bool = False,
    rounding: bool = False,
    group_by: Literal["ticker", "column"] = "ticker",
    adjusted: bool = False,
    **kwargs: Any,
) -> DataFrame:
    """Get yFinance OHLC data for any ticker and interval available."""
    # pylint: disable=import-outside-toplevel
    import yfinance as yf
    from dateutil.relativedelta import relativedelta
    from pandas import concat, to_datetime

    symbol = symbol.upper()
    _start_date = start_date
    intraday = False
    if interval in ["60m", "1h"]:
        period = "2y" if period in ["5y", "10y", "max"] else period
        _start_date = None
        intraday = True

    if interval in ["2m", "5m", "15m", "30m", "90m"]:
        _start_date = (datetime.now().date() - relativedelta(days=58)).strftime(
            "%Y-%m-%d"
        )
        intraday = True

    if interval == "1m":
        period = "5d"
        _start_date = None
        intraday = True

    if adjusted is False:
        kwargs = dict(auto_adjust=False, back_adjust=False)

    try:
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
            threads=False,
            **kwargs,
        )
    except ValueError as exc:
        raise EmptyDataError() from exc

    tickers = symbol.split(",")
    if len(tickers) > 1:
        _data = DataFrame()
        for ticker in tickers:
            temp = data[ticker].copy().dropna(how="all")
            if len(temp) > 0:
                temp.loc[:, "symbol"] = ticker
                temp = temp.reset_index().rename(
                    columns={"Date": "date", "Datetime": "date", "index": "date"}
                )
                _data = concat([_data, temp])
        if not _data.empty:
            index_keys = ["date", "symbol"] if "symbol" in _data.columns else "date"
            _data = _data.set_index(index_keys).sort_index()
            data = _data
    if not data.empty:
        data = data.reset_index()
        data = data.rename(columns={"Date": "date", "Datetime": "date"})
        data["date"] = data["date"].apply(to_datetime)
        data = data[data["Open"] > 0]
        if start_date is not None:
            data = data[data["date"] >= to_datetime(start_date)]
        if (
            end_date is not None
            and start_date is not None
            and to_datetime(end_date) > to_datetime(start_date)
        ):
            data = data[
                data["date"]
                <= (
                    to_datetime(end_date)
                    + relativedelta(minutes=719 if intraday is True else 0)
                )
            ]
        if intraday is True:
            data["date"] = data["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["date"] = data["date"].dt.strftime("%Y-%m-%d")
        if adjusted is False:
            data = data.drop(columns=["Adj Close"])
        data.columns = data.columns.str.lower().str.replace(" ", "_").to_list()
    return data


def df_transform_numbers(data: DataFrame, columns: list) -> DataFrame:
    """Replace abbreviations of numbers with actual numbers."""
    multipliers = {"M": 1e6, "B": 1e9, "T": 1e12}

    def replace_suffix(x, suffix, multiplier):
        return float(str(x).replace(suffix, "")) * multiplier if suffix in str(x) else x

    for col in columns:
        if col == "% Change":
            data[col] = data[col].astype(str).str.replace("%", "").astype(float)
        else:
            for suffix, multiplier in multipliers.items():
                data[col] = data[col].apply(replace_suffix, args=(suffix, multiplier))

    return data
