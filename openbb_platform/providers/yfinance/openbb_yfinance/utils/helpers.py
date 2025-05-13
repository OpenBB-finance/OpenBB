"""Yahoo Finance helpers module."""

# pylint: disable=unused-argument,too-many-arguments,too-many-branches,too-many-locals,too-many-statements

from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from openbb_core.provider.utils.errors import EmptyDataError
from openbb_yfinance.utils.references import INTERVALS, MONTHS, PERIODS

if TYPE_CHECKING:
    from datetime import date  # noqa
    from pandas import DataFrame


MONTH_MAP = {
    "F": "01",
    "G": "02",
    "H": "03",
    "J": "04",
    "K": "05",
    "M": "06",
    "N": "07",
    "Q": "08",
    "U": "09",
    "V": "10",
    "X": "11",
    "Z": "12",
}

PREDEFINED_SCREENERS = [
    "aggressive_small_caps",
    "day_gainers",
    "day_losers",
    "growth_technology_stocks",
    "most_actives",
    "most_shorted_stocks",
    "small_cap_gainers",
    "undervalued_growth_stocks",
    "undervalued_large_caps",
    "conservative_foreign_funds",
    "high_yield_bond",
    "portfolio_anchors",
    "solid_large_growth_funds",
    "solid_midcap_growth_funds",
    "top_mutual_funds",
]

SCREENER_FIELDS = [
    "symbol",
    "shortName",
    "regularMarketPrice",
    "regularMarketChange",
    "regularMarketChangePercent",
    "regularMarketVolume",
    "regularMarketOpen",
    "regularMarketDayHigh",
    "regularMarketDayLow",
    "regularMarketPreviousClose",
    "fiftyDayAverage",
    "twoHundredDayAverage",
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",
    "marketCap",
    "sharesOutstanding",
    "epsTrailingTwelveMonths",
    "forwardPE",
    "epsForward",
    "bookValue",
    "priceToBook",
    "trailingAnnualDividendYield",
    "currency",
    "exchange",
    "exchangeTimezoneName",
    "earnings_date",
]


async def get_custom_screener(
    body: dict[str, Any],
    limit: Optional[int] = None,
    region: str = "US",
):
    """Get a custom screener."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import (  # noqa
        get_requests_session,
        safe_fromtimestamp,
    )
    from curl_adapter import CurlCffiAdapter
    from pytz import timezone
    from yfinance.data import YfData

    session = get_requests_session()
    session.mount("https://", CurlCffiAdapter())
    session.mount("http://", CurlCffiAdapter())

    params_dict = {
        "corsDomain": "finance.yahoo.com",
        "formatted": "false",
        "lang": "en-US",
        "region": region,
    }
    _data = YfData(session=session)
    results: list = []
    body = body.copy()
    response = _data.post(
        "https://query2.finance.yahoo.com/v1/finance/screener",
        body=body,
        params=params_dict,
    )
    response.raise_for_status()
    res = response.json()["finance"]["result"][0]

    if not res.get("quotes"):
        raise EmptyDataError("No data found for the predefined screener.")

    results.extend(res["quotes"])
    total_results = res["total"]

    while len(results) < total_results:
        if limit is not None and len(results) >= limit:
            break
        offset = len(results)
        body["offset"] = offset
        response = _data.post(
            "https://query2.finance.yahoo.com/v1/finance/screener",
            body=body,
            params=params_dict,
        )
        if not res:
            break
        res = response.json()["finance"]["result"][0]
        results.extend(res.get("quotes", []))

    output: list = []

    for item in results:
        tz = item["exchangeTimezoneName"]
        earnings_date = (
            safe_fromtimestamp(item["earningsTimestamp"], timezone(tz)).strftime(  # type: ignore
                "%Y-%m-%d %H:%M:%S%z"
            )
            if item.get("earningsTimestamp")
            else None
        )
        item["earnings_date"] = earnings_date
        result = {k: item.get(k, None) for k in SCREENER_FIELDS}
        if result.get("regularMarketChange") and result.get("regularMarketVolume"):
            output.append(result)

    return output[:limit] if limit is not None else output


async def get_defined_screener(
    name: Optional[str] = None,
    body: Optional[dict[str, Any]] = None,
    limit: Optional[int] = None,
):
    """Get a predefined screener."""
    # pylint: disable=import-outside-toplevel
    import yfinance as yf  # noqa
    from curl_adapter import CurlCffiAdapter
    from openbb_core.provider.utils.helpers import (
        get_requests_session,
        safe_fromtimestamp,
    )
    from pytz import timezone

    if name and name not in PREDEFINED_SCREENERS:
        raise ValueError(
            f"Invalid predefined screener name: {name}\n    Valid names: {PREDEFINED_SCREENERS}"
        )

    results: list = []
    session = get_requests_session()
    session.mount("https://", CurlCffiAdapter())
    session.mount("http://", CurlCffiAdapter())

    offset = 0

    response = yf.screen(
        name,
        session=session,
        size=250,
        offset=offset,
    )

    if not response.get("quotes"):
        raise EmptyDataError("No data found for the predefined screener.")

    total_results = response["total"]
    results.extend(response["quotes"])

    while len(results) < total_results:
        if limit is not None and len(results) >= limit:
            break
        offset = len(results)
        res = yf.screen(
            name,
            session=session,
            size=250,
            offset=offset,
        )
        if not res:
            break
        results.extend(res.get("quotes", []))

    output: list = []
    symbols: set = set()

    for item in results:
        sym = item.get("symbol")

        if not sym or sym in symbols:
            continue

        symbols.add(sym)
        tz = item["exchangeTimezoneName"]
        earnings_date = (
            safe_fromtimestamp(item["earningsTimestamp"], timezone(tz)).strftime(  # type: ignore
                "%Y-%m-%d %H:%M:%S%z"
            )
            if item.get("earningsTimestamp")
            else None
        )
        item["earnings_date"] = earnings_date
        result = {k: item.get(k, None) for k in SCREENER_FIELDS}

        if result.get("regularMarketChange") and result.get("regularMarketVolume"):
            output.append(result)

        if not output:
            raise EmptyDataError("No data found for the predefined screener.")

    return output[:limit] if limit is not None else output


def get_expiration_month(symbol: str) -> str:
    """Get the expiration month for a given symbol."""
    month = symbol.split(".")[0][-3]
    year = "20" + symbol.split(".")[0][-2:]
    return f"{year}-{MONTH_MAP[month]}"


def get_futures_data() -> "DataFrame":
    """Return the dataframe of the futures csv file."""
    # pylint: disable=import-outside-toplevel
    from pathlib import Path  # noqa
    from pandas import read_csv  # noqa

    return read_csv(Path(__file__).resolve().parent / "futures.csv")


def get_futures_symbols(symbol: str) -> list:
    """Get the list of futures symbols from the continuation symbol."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import get_requests_session  # noqa
    from curl_adapter import CurlCffiAdapter
    from yfinance.data import YfData

    _symbol = symbol.upper() + "%3DF"
    URL = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{_symbol}"
    params = {"modules": "futuresChain"}

    session = get_requests_session()
    session.mount("https://", CurlCffiAdapter())
    session.mount("http://", CurlCffiAdapter())

    response: dict = YfData(session=session).get_raw_json(url=URL, params=params)
    futures_symbols: list = []

    if "quoteSummary" in response:
        result = response["quoteSummary"].get("result", [])
        if not result:
            raise ValueError(f"No futures chain found for, {symbol}")
        futures = result[0].get("futuresChain", {})
        if futures:
            futures_symbols = futures.get("futures", [])

    return futures_symbols


async def get_futures_quotes(symbols: list) -> "DataFrame":
    """Get the current futures quotes for a list of symbols."""
    # pylint: disable=import-outside-toplevel
    import os  # noqa
    from contextlib import (
        contextmanager,
        redirect_stderr,
        redirect_stdout,
        suppress,
    )  # noqa
    from aiohttp import ClientError  # noqa
    from openbb_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher  # noqa
    from pandas import DataFrame  # noqa

    @contextmanager
    def suppress_all_output():
        with open(os.devnull, "w") as devnull, redirect_stdout(
            devnull
        ), redirect_stderr(devnull):
            yield

    with suppress_all_output(), suppress(ClientError):
        fetcher = YFinanceEquityQuoteFetcher()
        data = await fetcher.fetch_data(
            params={"symbol": ",".join(symbols)}, credentials={}
        )

    df = DataFrame([d.model_dump() for d in data])  # type: ignore
    prices = df[["symbol", "bid", "ask", "prev_close"]].copy()
    prices.loc[:, "price"] = round((prices.ask + prices.bid) / 2, 2)
    prices.price = prices.price.fillna(prices.prev_close)
    prices["expiration"] = [get_expiration_month(symbol) for symbol in prices.symbol]

    return prices[["expiration", "price"]]  # type: ignore


async def get_historical_futures_prices(
    symbols: list, start_date: "date", end_date: "date"
):
    """Get historical futures prices for the list of symbols."""
    # pylint: disable=import-outside-toplevel
    from openbb_yfinance.models.equity_historical import (  # noqa
        YFinanceEquityHistoricalFetcher,
    )

    fetcher = YFinanceEquityHistoricalFetcher()

    return await fetcher.fetch_data(
        params={
            "symbol": ",".join(symbols),
            "start_date": start_date,
            "end_date": end_date,
        },
        credentials={},
    )


async def get_futures_curve(  # pylint: disable=too-many-return-statements
    symbol: str, date: Optional[Union[str, list]] = None
) -> "DataFrame":
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
    from datetime import date as dateType, datetime  # noqa
    from dateutil.relativedelta import relativedelta  # noqa
    from pandas import Categorical, DataFrame, DatetimeIndex, to_datetime  # noqa

    futures_symbols = get_futures_symbols(symbol)
    today = datetime.today().date()
    dates: list = []
    if date:
        if isinstance(date, dateType):
            date = date.strftime("%Y-%m-%d")
        if isinstance(date, list) and isinstance(date[0], dateType):
            date = [d.strftime("%Y-%m-%d") for d in date]
        dates = date.split(",") if isinstance(date, str) else date
        dates = sorted([to_datetime(d).date() for d in dates])

    if futures_symbols and (not date or len(dates) == 1 and dates[0] >= today):
        futures_quotes = await get_futures_quotes(futures_symbols)
        return futures_quotes

    if dates and futures_symbols:
        historical_futures_prices = await get_historical_futures_prices(
            futures_symbols, dates[0], dates[-1]
        )
        df = DataFrame([d.model_dump() for d in historical_futures_prices])  # type: ignore
        df = df.set_index("date").sort_index()
        df.index = df.index.astype(str)
        df.index = DatetimeIndex(df.index)
        dates_list = DatetimeIndex(dates)
        symbols = df.symbol.unique().tolist()
        expiration_dict = {symbol: get_expiration_month(symbol) for symbol in symbols}
        df = (
            df.reset_index()
            .pivot(columns="symbol", values="close", index="date")  # type: ignore
            .copy()
        )
        df = df.rename(columns=expiration_dict)
        df.columns.name = "expiration"

        # Find the nearest date in the DataFrame to each date in dates_list
        nearest_dates = [df.index.asof(date) for date in dates_list]

        # Filter for only the nearest dates
        df = df[df.index.isin(nearest_dates)]

        df = df.fillna("N/A").replace("N/A", None)

        # Flatten the DataFrame
        flattened_data = df.reset_index().melt(
            id_vars="date", var_name="expiration", value_name="price"
        )
        flattened_data = flattened_data.sort_values("date")
        flattened_data["expiration"] = Categorical(
            flattened_data["expiration"],
            categories=sorted(list(expiration_dict.values())),
            ordered=True,
        )
        flattened_data = flattened_data.sort_values(
            by=["date", "expiration"]
        ).reset_index(drop=True)
        flattened_data.loc[:, "date"] = flattened_data["date"].dt.strftime("%Y-%m-%d")

        return flattened_data

    if not futures_symbols:
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        from contextlib import contextmanager, redirect_stderr, redirect_stdout  # noqa

        futures_data = get_futures_data()
        try:
            exchange = futures_data[futures_data["Ticker"] == symbol][
                "Exchange"
            ].values[  # type: ignore
                0
            ]
        except IndexError as exc:
            raise ValueError(f"Symbol {symbol} was not found.") from exc

        futures_index: list = []
        futures_curve: list = []
        futures_date: list = []
        historical_curve: list = []
        if dates:
            dates = [d.strftime("%Y-%m-%d") for d in dates]
            dates_list = DatetimeIndex(dates)

        i = 0
        empty_count = 0

        @contextmanager
        def suppress_all_output():
            with open(os.devnull, "w") as devnull, redirect_stdout(
                devnull
            ), redirect_stderr(devnull):
                yield

        with suppress_all_output():
            while empty_count < 12:
                future = today + relativedelta(months=i)
                future_symbol = (
                    f"{symbol}{MONTHS[future.month]}{str(future.year)[-2:]}.{exchange}"
                )
                data = yf_download(future_symbol)
                if data.empty:
                    empty_count += 1
                else:
                    empty_count = 0
                    if dates:
                        data = data.set_index("date").sort_index()
                        data.index = DatetimeIndex(data.index)
                        nearest_dates = [data.index.asof(date) for date in dates_list]
                        data = data[data.index.isin(nearest_dates)]
                        data.index = data.index.strftime("%Y-%m-%d")  # type: ignore
                        for dt in dates:
                            try:
                                historical_curve.append(data.loc[dt, "close"])
                                futures_date.append(dt)
                                futures_index.append(future.strftime("%Y-%m"))
                            except KeyError:
                                historical_curve.append(None)
                    else:
                        futures_index.append(future.strftime("%Y-%m"))
                        futures_curve.append(
                            data.query("close.notnull()")["close"].values[-1]
                        )

                i += 1

        if not futures_index:
            raise EmptyDataError()

        if historical_curve:
            df = DataFrame(
                {
                    "date": futures_date,
                    "price": historical_curve,
                    "expiration": futures_index,
                }
            )
            df["expiration"] = Categorical(
                df["expiration"],
                categories=sorted(list(set(futures_index))),
                ordered=True,
            )
            df = df.sort_values(by=["date", "expiration"]).reset_index(drop=True)
            if len(df.date.unique()) == 1:
                df = df.drop(columns=["date"])

            return df

    return DataFrame({"price": futures_curve, "expiration": futures_index})


def yf_download(  # pylint: disable=too-many-positional-arguments
    symbol: str,
    start_date: Optional[Union[str, "date"]] = None,
    end_date: Optional[Union[str, "date"]] = None,
    interval: INTERVALS = "1d",
    period: Optional[PERIODS] = None,
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
) -> "DataFrame":
    """Get yFinance OHLC data for any ticker and interval available."""
    # pylint: disable=import-outside-toplevel
    from datetime import datetime, timedelta  # noqa
    from curl_adapter import CurlCffiAdapter
    from openbb_core.provider.utils.helpers import get_requests_session
    from pandas import DataFrame, concat, to_datetime
    import yfinance as yf

    symbol = symbol.upper()
    _start_date = start_date
    intraday = False
    if interval in ["60m", "1h"]:
        period = "2y" if period in ["5y", "10y", "max"] else period
        _start_date = None
        intraday = True

    if interval in ["2m", "5m", "15m", "30m", "90m"]:
        _start_date = (datetime.now().date() - timedelta(days=58)).strftime("%Y-%m-%d")
        intraday = True

    if interval == "1m":
        period = "5d"
        _start_date = None
        intraday = True

    if adjusted is False:
        kwargs.update(dict(auto_adjust=False, back_adjust=False, period=period))

    session = kwargs.pop("session", None) or get_requests_session()
    session.mount("https://", CurlCffiAdapter())
    session.mount("http://", CurlCffiAdapter())

    if session.proxies:
        kwargs["proxy"] = session.proxies
    try:
        data = yf.download(
            tickers=symbol,
            start=_start_date,
            end=None,
            interval=interval,
            prepost=prepost,
            actions=actions,
            progress=progress,
            ignore_tz=ignore_tz,
            keepna=keepna,
            repair=repair,
            rounding=rounding,
            group_by=group_by,
            threads=False,
            session=session,
            **kwargs,
        )
        if hasattr(data.index, "tz") and data.index.tz is not None:
            data = data.tz_convert(None)

    except ValueError as exc:
        raise EmptyDataError() from exc

    tickers = symbol.split(",")
    if len(tickers) == 1:
        data = data.get(symbol, DataFrame())
    elif len(tickers) > 1:
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

    if data.empty:
        raise EmptyDataError()

    data = data.reset_index()
    data = data.rename(columns={"Date": "date", "Datetime": "date"})
    data["date"] = data["date"].apply(to_datetime)
    data = data[data["Open"] > 0]

    if start_date is not None:
        data = data[data["date"] >= to_datetime(start_date)]  # type: ignore
    if (
        end_date is not None
        and start_date is not None
        and to_datetime(end_date) > to_datetime(start_date)  # type: ignore
    ):
        data = data[
            data["date"]
            <= (
                to_datetime(end_date)  # type: ignore
                + timedelta(days=1 if intraday is True else 0)
            )
        ]
    if intraday is True:
        data["date"] = data["date"].dt.strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
    else:
        data["date"] = data["date"].dt.strftime("%Y-%m-%d")  # type: ignore
    if adjusted is False:
        data = data.drop(columns=["Adj Close"])  # type: ignore
    data.columns = data.columns.str.lower().str.replace(" ", "_").to_list()  # type: ignore

    # Remove columns with no information.
    for col in ["dividends", "capital_gains", "stock_splits"]:
        if col in data.columns and data[col].sum() == 0:
            data = data.drop(columns=[col])

    return data  # type: ignore


def df_transform_numbers(data: "DataFrame", columns: list) -> "DataFrame":
    """Replace abbreviations of numbers with actual numbers."""
    multipliers = {"M": 1e6, "B": 1e9, "T": 1e12}

    def replace_suffix(x, suffix, multiplier):
        return float(str(x).replace(suffix, "")) * multiplier if suffix in str(x) else x

    for col in columns:
        if col == "% Change":
            data[col] = data[col].astype(str).str.replace("%", "").astype(float) / 100
        else:
            for suffix, multiplier in multipliers.items():
                data[col] = data[col].apply(replace_suffix, args=(suffix, multiplier))

    return data
