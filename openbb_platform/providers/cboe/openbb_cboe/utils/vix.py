"""Cboe VIX Futures Utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pandas import DataFrame


VX_AM_SYMBOLS = [
    "TWLV1",
    "TWLV2",
    "TWLV3",
    "TWLV4",
    "TWLV5",
    "TWLV6",
    "TWLV7",
    "TWLV8",
    "TWLV9",
]

VX_EOD_SYMBOL_TO_MONTH = {
    "UZF": 1,
    "UZG": 2,
    "UZH": 3,
    "UZJ": 4,
    "UZK": 5,
    "UZM": 6,
    "UZN": 7,
    "UZQ": 8,
    "UZU": 9,
    "UZV": 10,
    "UZX": 11,
    "UZZ": 12,
}

VX_EOD_SYMBOLS = list(VX_EOD_SYMBOL_TO_MONTH)


def get_front_month(date: str | None = None) -> int:
    """Get the front month, rolling on the third Wednesday of the month.

    Parameters
    ----------
    date : str | None
        The reference date, [YYYY-MM-DD]. Defaults to today.

    Returns
    -------
    int
        The front-month number, 1-12.
    """
    from calendar import monthcalendar
    from datetime import datetime

    from openbb_cboe.utils.helpers import ny_now

    today = ny_now() if date is None else datetime.strptime(date, "%Y-%m-%d")
    third_wednesday = [
        week[2] for week in monthcalendar(today.year, today.month) if week[2] != 0
    ][2]

    if today.day > third_wednesday:
        return (today.month % 12) + 1

    return today.month


def get_vx_symbols(date: str | None = None) -> dict[str, str]:
    """Map the VX1-VX12 relative contracts to Cboe EOD symbols.

    Parameters
    ----------
    date : str | None
        The reference date, [YYYY-MM-DD]. Defaults to today.

    Returns
    -------
    dict[str, str]
        Relative contract name mapped to the Cboe symbol.
    """
    from collections import deque

    symbols = deque(VX_EOD_SYMBOLS)
    symbols.rotate(-(get_front_month(date) - 1))

    return {f"VX{i + 1}": symbol for i, symbol in enumerate(symbols)}


def get_months(front_month: int) -> dict[str, int]:
    """Map the VX1-VX12 relative contracts to forward expiration months.

    Parameters
    ----------
    front_month : int
        The front-month number, 1-12.

    Returns
    -------
    dict[str, int]
        Relative contract name mapped to the calendar month.
    """
    from collections import deque

    front_month = front_month % 12
    months = deque([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    months.rotate(-front_month + 1)

    return {f"VX{i + 1}": month for i, month in enumerate(months)}


def check_date(date):
    """Roll a weekend date back to the preceding Friday.

    Parameters
    ----------
    date : datetime
        The date to check.

    Returns
    -------
    datetime
        The nearest preceding weekday.
    """
    from datetime import timedelta

    weekday = date.date().weekday()

    return date if weekday < 5 else date - timedelta(days=weekday - 4)


async def get_vx_current(
    vx_type: Literal["am", "eod"] = "eod", use_cache: bool = True
) -> DataFrame:
    """Get the current quotes for VX futures.

    Parameters
    ----------
    vx_type : Literal["am", "eod"]
        The type of VX futures to get. 'am' is the mid-morning TWAP value,
        'eod' is the end-of-day value.
    use_cache : bool
        When True, the symbol directories are cached on disk for 24 hours.

    Returns
    -------
    DataFrame
        Expiration and price for the current VX futures curve.

    Raises
    ------
    OpenBBError
        If ``vx_type`` is not 'am' or 'eod'.
    """
    from datetime import datetime

    from openbb_core.app.model.abstract.error import OpenBBError
    from pandas import DataFrame

    from openbb_cboe.models.equity_quote import CboeEquityQuoteFetcher

    if vx_type not in ["am", "eod"]:
        raise OpenBBError("vx_type must be one of: 'am', 'eod'")

    current_symbols = list(get_vx_symbols().values())[:9]
    symbols = VX_AM_SYMBOLS if vx_type == "am" else current_symbols
    current_months = [VX_EOD_SYMBOL_TO_MONTH.get(d) for d in current_symbols]
    current_year = datetime.today().year
    data = await CboeEquityQuoteFetcher.fetch_data(
        {"symbol": ",".join(symbols), "use_cache": use_cache}, {}
    )
    df = DataFrame([d.model_dump() for d in data])  # ty: ignore[unresolved-attribute]

    if vx_type == "am":
        df = df[["symbol", "last_price"]]
    else:
        df = df.sort_values(by="last_timestamp", ascending=False)[
            ["symbol", "last_price"]
        ]
        df = df.set_index("symbol")
        df = df.filter(items=current_symbols, axis=0).reset_index()
        df = df.rename(columns={"index": "symbol"})

    expirations: list = []

    for month in current_months:
        new_year = month == 1
        current_year = (
            current_year + 1
            if new_year and datetime.today().month != 1
            else current_year
        )
        new_month = f"0{month}" if month < 10 else str(month)  # ty: ignore[unsupported-operator]
        expirations.append(f"{current_year}-{new_month}")

    df.symbol = expirations

    return df.rename(columns={"symbol": "expiration", "last_price": "price"}).dropna(
        how="any"
    )


async def get_vx_by_date(
    date: str | list[str],
    vx_type: Literal["am", "eod"] = "eod",
    use_cache: bool = True,
) -> DataFrame:
    """Get the VX futures curve as of one or more dates.

    Parameters
    ----------
    date : str | list[str]
        The date(s) to get VX futures for. A string may be comma-separated.
    vx_type : Literal["am", "eod"]
        The type of VX futures to get. 'am' is the mid-morning TWAP value,
        'eod' is the end-of-day value.
    use_cache : bool
        When True, the symbol directories are cached on disk for 24 hours.

    Returns
    -------
    DataFrame
        Date, expiration, symbol, and price for each requested date.

    Raises
    ------
    OpenBBError
        If ``vx_type`` is not 'am' or 'eod'.
    EmptyDataError
        If no data was returned for any requested date.
    """
    from datetime import datetime, timedelta

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError
    from pandas import Categorical, DataFrame, DatetimeIndex, concat, isna, to_datetime

    from openbb_cboe.models.equity_historical import CboeEquityHistoricalFetcher

    if vx_type not in ["am", "eod"]:
        raise OpenBBError("'vx_type' must be one of: 'am', 'eod'")

    symbols = list(get_vx_symbols().values()) if vx_type == "eod" else VX_AM_SYMBOLS
    dates = date.split(",") if isinstance(date, str) else date
    dates = sorted([check_date(to_datetime(d)) for d in dates])
    today = check_date(datetime.today()).strftime("%Y-%m-%d")

    if len(dates) == 1:
        new_date = check_date(to_datetime(dates[0]))

        if new_date.strftime("%Y-%m-%d") == today:
            df = await get_vx_current(vx_type=vx_type)
            df["date"] = new_date.strftime("%Y-%m-%d")
            return df

        end_date = new_date.strftime("%Y-%m-%d")
        start_date = (check_date(new_date - timedelta(days=1))).strftime("%Y-%m-%d")
    else:
        start_date = check_date(dates[0]).strftime("%Y-%m-%d")
        end_date = check_date(dates[-1]).strftime("%Y-%m-%d")

    current_data = DataFrame()

    if end_date == today:
        current_data = await get_vx_current(vx_type=vx_type)
        current_data["date"] = end_date
        current_data["symbol"] = [f"VX{i}" for i in range(1, 10)]

    data = await CboeEquityHistoricalFetcher.fetch_data(
        {
            "symbol": ",".join(symbols),
            "start_date": start_date,
            "end_date": end_date,
            "use_cache": use_cache,
        }
    )
    df = DataFrame([d.model_dump() for d in data])  # ty: ignore[unresolved-attribute]
    df = df.set_index("date").sort_index()
    df.index = df.index.astype(str)
    df.index = DatetimeIndex(df.index)
    dates_list = DatetimeIndex(dates)
    df = df.reset_index().pivot(columns="symbol", values="close", index="date").copy()

    if vx_type == "am":
        df = df.dropna(how="any")

    nearest_dates: list = []

    for date_ in dates_list:
        nearest_date = df.index.asof(date_)

        if isna(nearest_date):
            differences = abs(df.index - date_)
            nearest_date = df.index[differences.argmin()]

        nearest_dates.append(nearest_date)

    nearest_index = DatetimeIndex(nearest_dates)
    df = df[df.index.isin(nearest_index)]
    df = df.fillna("N/A").replace("N/A", None)
    df.index = df.index.astype(str)
    output = DataFrame()

    for _date in df.index.tolist():
        temp = df.filter(like=_date, axis=0).copy()
        current_symbols = (
            VX_AM_SYMBOLS
            if vx_type == "am"
            else list(get_vx_symbols(date=_date).values())[:9]
        )
        temp = temp.filter(items=current_symbols, axis=1)
        current_month = get_front_month(_date)
        current_months = get_months(current_month)
        current_year = int(_date.split("-")[0])
        expirations: list = []

        for month in list(current_months.values())[:9]:
            new_year = month == 1
            current_year = (
                current_year + 1 if new_year and current_month != 1 else current_year
            )
            new_month = f"0{month}" if month < 10 else str(month)
            expirations.append(f"{current_year}-{new_month}")

        flattened = temp.reset_index().melt(
            id_vars="date", var_name="expiration", value_name="price"
        )
        vx_symbols = (
            {item: item.replace("TWLV", "VX") for item in VX_AM_SYMBOLS}
            if vx_type == "am"
            else {v: k for k, v in get_vx_symbols(date=_date).items()}
        )
        flattened["symbol"] = flattened.expiration.map(vx_symbols)
        flattened.expiration = expirations
        flattened = flattened.dropna(how="any", subset=["price"])
        output = concat([output, flattened])

    if not current_data.empty and current_data.date[0] not in output.date.unique():
        output = concat([output, current_data])

    if output.empty:
        raise EmptyDataError()

    output = output.sort_values("date")
    dates = DatetimeIndex(dates)

    if dates[-1] != nearest_index[-1] and not current_data.empty:
        output = output[output.date != nearest_index[-1].strftime("%Y-%m-%d")]

    output["symbol"] = Categorical(
        output["symbol"],
        categories=sorted(output.symbol.unique().tolist()),
        ordered=True,
    )

    return (
        output.sort_values(by=["date", "symbol"])
        .reset_index(drop=True)
        .dropna(how="any")
    )
