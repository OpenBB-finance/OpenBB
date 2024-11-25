"""VIX Utilities."""

from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

if TYPE_CHECKING:
    from pandas import DataFrame  # pylint: disable=import-outside-toplevel


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


def get_front_month(date: Optional[str] = None):
    """Get the front month based on the third Wednesday of the month."""
    # pylint: disable=import-outside-toplevel
    from datetime import datetime  # noqa
    from calendar import monthcalendar

    today = datetime.now() if date is None else datetime.strptime(date, "%Y-%m-%d")
    third_wednesday = [
        week[2] for week in monthcalendar(today.year, today.month) if week[2] != 0
    ][2]
    if today.day > third_wednesday:
        # If today is after the third Wednesday of the month, return the next month
        return (today.month % 12) + 1
    # Otherwise, return the current month
    return today.month


def get_vx_symbols(date: Optional[str] = None) -> Dict:
    """Get the VIX symbols based on relative position to the front month."""
    # pylint: disable=import-outside-toplevel
    from collections import deque

    VIX_SYMBOLS = deque(
        [
            "UZF",  # Jan
            "UZG",  # Feb
            "UZH",  # Mar
            "UZJ",  # Apr
            "UZK",  # May
            "UZM",  # Jun
            "UZN",  # Jul
            "UZQ",  # Aug
            "UZU",  # Sep
            "UZV",  # Oct
            "UZX",  # Nov
            "UZZ",  # Dec
        ]
    )
    VIX_SYMBOLS.rotate(-(get_front_month(date) - 1))

    return {f"VX{i+1}": symbol for i, symbol in enumerate(VIX_SYMBOLS)}


def get_months(front_month):
    """Translate the front month into forward expiration dates."""
    # pylint: disable=import-outside-toplevel
    from collections import deque

    front_month = front_month % 12
    MONTHS = deque([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    MONTHS.rotate(-front_month + 1)

    return {f"VX{i+1}": month for i, month in enumerate(MONTHS)}


def check_date(date):
    """Check the date for weekdays."""
    # pylint: disable=import-outside-toplevel
    from datetime import timedelta

    return (
        date
        if date.date().weekday() < 5
        else date - timedelta(days=6 - date.date().weekday())
    )


async def get_vx_current(
    vx_type: Literal["am", "eod"] = "eod", use_cache: bool = True
) -> "DataFrame":
    """Get the current quotes for VX Futures.

    Parameters
    ----------
    vx_type : Literal["am", "eod"]
        The type of VX futures to get. Default is "eod".
            am: Mid-morning TWAP value
            eod: End-of-day value
    use_cache : bool
        Whether to use the cache. Default is True. Cache is only used for symbol mapping.

    Returns
    -------
    DataFrame
        DataFrame with the current VX futures data.
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_cboe.models.equity_quote import CboeEquityQuoteFetcher
    from pandas import DataFrame

    if vx_type not in ["am", "eod"]:
        raise OpenBBError("vx_type must be one of: 'am', 'eod'")

    current_symbols = list(get_vx_symbols().values())[:9]
    symbols = VX_AM_SYMBOLS if vx_type == "am" else current_symbols
    current_months = [VX_EOD_SYMBOL_TO_MONTH.get(d) for d in current_symbols]
    current_year = datetime.today().year
    data = await CboeEquityQuoteFetcher.fetch_data(
        {"symbol": ",".join(symbols), "use_cache": use_cache}, {}
    )
    df = DataFrame([d.model_dump() for d in data])  # type: ignore

    if vx_type == "am":
        df = df[["symbol", "last_price"]]
    elif vx_type == "eod":
        df = df.sort_values(by="last_timestamp", ascending=False)[
            ["symbol", "last_price"]
        ]
        df = df.set_index("symbol")
        df = df.filter(items=current_symbols, axis=0).reset_index()
        df = df.rename(columns={"index": "symbol"})

    expirations: List = []
    for month in current_months:
        new_year = month == 1
        current_year = (
            current_year + 1
            if new_year and datetime.today().month != 1
            else current_year
        )
        new_month = "0" + str(month) if month < 10 else str(month)  # type: ignore
        expirations.append(f"{current_year}-{new_month}")

    df.symbol = expirations
    df = df.rename(columns={"symbol": "expiration", "last_price": "price"})

    return df


# pylint: disable=too-many-locals
async def get_vx_by_date(
    date: Union[str, List[str]],
    vx_type: Literal["am", "eod"] = "eod",
    use_cache: bool = True,
) -> "DataFrame":
    """Get VX futures by date(s).

    Parameters
    ----------
    date : str or List[str]
        The date(s) to get VX futures for.
    vx_type : Literal["am", "eod"]
        The type of VX futures to get. Default is "eod".
            am: Mid-morning TWAP value
            eod: End-of-day value
    use_cache : bool
        Whether to use the cache. Default is True. Cache is only used for symbol mapping.

    Returns
    -------
    DataFrame
        Categorical DataFrame with VX futures data for the given date(s).
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime, timedelta  # noqa
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError
    from openbb_cboe.models.equity_historical import CboeEquityHistoricalFetcher
    from pandas import Categorical, DataFrame, DatetimeIndex, concat, isna, to_datetime

    if vx_type not in ["am", "eod"]:
        raise OpenBBError("'vx_type' must be one of: 'am', 'eod'")

    df = DataFrame()
    start_date = ""
    end_date = ""
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

    # The data from the current date is not available in the historical data,
    # so we need to get it separately, if required.
    current_data = DataFrame()

    if end_date == today:
        current_data = await get_vx_current(vx_type=vx_type)
        current_data["date"] = end_date
        current_data["symbol"] = [
            "VX1",
            "VX2",
            "VX3",
            "VX4",
            "VX5",
            "VX6",
            "VX7",
            "VX8",
            "VX9",
        ]

    data = await CboeEquityHistoricalFetcher.fetch_data(
        {
            "symbol": ",".join(symbols),
            "start_date": start_date,
            "end_date": end_date,
            "use_cache": use_cache,
        }
    )
    df = DataFrame([d.model_dump() for d in data])  # type: ignore
    df = df.set_index("date").sort_index()

    df.index = df.index.astype(str)
    df.index = DatetimeIndex(df.index)
    dates_list = DatetimeIndex(dates)
    symbols = df.symbol.unique().tolist()
    df = (
        df.reset_index()
        .pivot(columns="symbol", values="close", index="date")  # type: ignore
        .copy()
    )
    if vx_type == "am":
        df = df.dropna(how="any")

    nearest_dates = []
    for date_ in dates_list:
        nearest_date = df.index.asof(date_)
        if isna(nearest_date):  # type: ignore
            differences = abs(df.index - date_)
            min_diff_index = differences.argmin()
            nearest_date = df.index[min_diff_index]
        nearest_dates.append(nearest_date)
    nearest_dates = DatetimeIndex(nearest_dates)

    # Filter for only the nearest dates
    df = df[df.index.isin(nearest_dates)]
    df = df.fillna("N/A").replace("N/A", None)
    output = DataFrame()
    df.index = df.index.astype(str)
    # For each date, we need to arrange VX1 - VX9 according to the relative front month.
    for _date in df.index.tolist():
        temp = df.filter(like=_date, axis=0).copy()
        current_symbols = list(get_vx_symbols(date=_date).values())[:9]
        current_symbols = VX_AM_SYMBOLS if vx_type == "am" else current_symbols
        temp = temp.filter(items=current_symbols, axis=1)
        current_month = get_front_month(_date)
        current_months = get_months(current_month)
        current_year = int(_date.split("-")[0])
        expirations: List = []
        for month in list(current_months.values())[:9]:
            new_year = month == 1
            current_year = (
                current_year + 1 if new_year and current_month != 1 else current_year
            )
            new_month = "0" + str(month) if month < 10 else str(month)  # type: ignore
            expirations.append(f"{current_year}-{new_month}")
        flattened = temp.reset_index().melt(
            id_vars="date", var_name="expiration", value_name="price"
        )
        if vx_type == "eod":
            vx_symbols = {v: k for k, v in get_vx_symbols(date=_date).items()}
        elif vx_type == "am":
            vx_symbols = {item: item.replace("TWLV", "VX") for item in VX_AM_SYMBOLS}
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
    if dates[-1] != nearest_dates[-1] and not current_data.empty:
        output = output[output.date != nearest_dates[-1].strftime("%Y-%m-%d")]  # type: ignore
    output["symbol"] = Categorical(
        output["symbol"],
        categories=sorted(output.symbol.unique().tolist()),
        ordered=True,
    )
    output = output.sort_values(by=["date", "symbol"]).reset_index(drop=True)

    return output
