"""Deribit Helpers Module."""

from typing import Literal

from async_lru import alru_cache
from openbb_core.app.model.abstract.error import OpenBBError

DERIBIT_OPTIONS_SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "BNB", "PAXG"]
OptionsSymbols = Literal["BTC", "ETH", "SOL", "XRP", "BNB", "PAXG"]
CURRENCIES = ["BTC", "ETH", "USDC", "USDT", "EURR", "all"]
Currencies = Literal["BTC", "ETH", "USDC", "USDT", "EURR", "all"]
DERIVATIVE_TYPES = ["future", "option", "spot", "future_combo", "option_combo"]
DerivativeTypes = Literal["future", "option", "spot", "future_combo", "option_combo"]
DERIBIT_FUTURES_CURVE_SYMBOLS = ["BTC", "ETH", "PAXG"]
FuturesCurveSymbols = Literal["BTC", "ETH", "PAXG"]
BASE_URL = "https://www.deribit.com"

DERIBIT_INTERVALS = [
    "1m",
    "3m",
    "5m",
    "10m",
    "15m",
    "30m",
    "1h",
    "2h",
    "3h",
    "6h",
    "12h",
    "1d",
]
DeribitIntervals = Literal[
    "1m", "3m", "5m", "10m", "15m", "30m", "1h", "2h", "3h", "6h", "12h", "1d"
]
INTERVAL_MAP = {
    "1m": "1",
    "3m": "3",
    "5m": "5",
    "10m": "10",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "3h": "180",
    "6h": "360",
    "12h": "720",
    "1d": "1D",
}


@alru_cache(maxsize=64)
async def get_instruments(
    currency: Currencies = "BTC",
    derivative_type: DerivativeTypes | None = None,
    expired: bool = False,
) -> list[dict]:
    """
    Get Deribit instruments.

    Parameters
    ----------
    currency : Currencies
        The currency to get instruments for. Default is "BTC".
    derivative_type : Optional[DerivativeTypes]
        The type of derivative to get instruments for. Default is None, which gets all types.

    Returns
    -------
    list[dict]
        A list of instrument dictionaries.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    if currency != "all" and currency.upper() not in CURRENCIES:
        raise ValueError(
            f"Currency {currency} not supported. Supported currencies are: {', '.join(CURRENCIES)}"
        )
    if derivative_type and derivative_type not in DERIVATIVE_TYPES:
        raise ValueError(
            f"Kind {derivative_type} not supported. Supported kinds are: {', '.join(DERIVATIVE_TYPES)}"
        )

    url = f"{BASE_URL}/api/v2/public/get_instruments?currency={currency.upper() if currency != 'all' else 'any'}"

    if derivative_type is not None:
        url += f"&kind={derivative_type}"

    if expired:
        url += f"&expired={str(expired).lower()}"

    try:
        response = await amake_request(url)
        return response.get("result", [])  # type: ignore
    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(
            f"Failed to get instruments -> {e.__class__.__name__}: {e}"
        ) from e


async def get_options_symbols(symbol: OptionsSymbols = "BTC") -> dict:
    """
    Get a dictionary of contract symbols by expiry.

    Parameters
    ----------
    symbol : OptionsSymbols
        The underlying symbol to get options for. Default is "btc".

    Returns
    -------
    dict[str, str]
        A dictionary of contract symbols by expiry date.
    """
    # pylint: disable=import-outside-toplevel
    from pandas import to_datetime

    if symbol.upper() not in DERIBIT_OPTIONS_SYMBOLS:
        raise ValueError(
            f"Invalid Deribit symbol. Supported symbols are: {', '.join(DERIBIT_OPTIONS_SYMBOLS)}",
        )

    currency = (
        "USDC" if symbol.upper() in ["BNB", "PAXG", "SOL", "XRP"] else symbol.upper()
    )
    instruments = await get_instruments(currency, "option")
    expirations: dict = {}
    all_options = list(
        set(
            d.get("instrument_name")
            for d in instruments
            if d.get("instrument_name").startswith(symbol)
            and d.get("instrument_name").endswith(("-C", "-P"))
        )
    )
    for item in sorted(
        list(
            set(
                (
                    to_datetime(d.split("-")[1]).date().strftime("%Y-%m-%d"),
                    d.split("-")[1],
                )
                for d in all_options
            )
        )
    ):
        expirations[item[0]] = item[1]

    return {k: [d for d in all_options if v in d] for k, v in expirations.items()}


async def get_futures_curve_symbols(symbol: FuturesCurveSymbols = "BTC") -> list[str]:
    """
    Get a list of futures symbols for a given symbol.

    Parameters
    ----------
    symbol : FuturesCurveSymbols
        The symbol to get futures symbols for.

    Returns
    -------
    list[str]
        A list of futures symbols.
    """
    symbol = symbol.upper()  # type: ignore
    if symbol not in DERIBIT_FUTURES_CURVE_SYMBOLS:
        raise ValueError(
            f"Invalid Deribit symbol. Supported symbols are: {', '.join(DERIBIT_FUTURES_CURVE_SYMBOLS)}",
        )

    currency = "USDC" if symbol == "PAXG" else symbol
    instruments = await get_instruments(currency, "future")

    symbols: list = []
    for d in instruments:
        ins_name = d.get("instrument_name", "")
        if ins_name.startswith(symbol):
            symbols.append(ins_name)

    return symbols


async def get_ticker_data(symbol: str) -> dict:
    """
    Get ticker data.

    Parameters
    ----------
    symbol : str
        The symbol to get ticker data for.

    Returns
    -------
    dict
        The ticker data.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import amake_request

    url = f"{BASE_URL}/api/v2/public/ticker?instrument_name={symbol}"

    try:
        response = await amake_request(url)
        if response.get("error"):  # type: ignore[union-attr]
            raise OpenBBError(response.get("error"))  # type: ignore[union-attr]
        data = response.get("result", {})  # type: ignore[union-attr]
        stats = data.pop("stats", {})
        return {**data, **stats}

    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(f"Failed to get ticker data -> {e}: {e.args[0]}") from e


async def get_perpetual_symbols() -> dict:
    """
    Get perpetual symbols.

    Returns
    -------
    dict
        A dictionary of short symbols to full perpetual symbols.
    """
    instruments = await get_instruments("all", "future")
    return {
        d["instrument_name"].split("-")[0].replace("_", ""): d["instrument_name"]
        for d in instruments
        if d.get("settlement_period") == "perpetual"
    }


async def get_ohlc_data(
    symbol: str, start_date: str, end_date: str, interval: DeribitIntervals = "1d"
) -> list[dict]:
    """Get OHLC data for a given symbol. Enter dates in the format 'YYYY-MM-DD'."""
    # pylint: disable=import-outside-toplevel
    import asyncio  # noqa
    from openbb_core.provider.utils.errors import EmptyDataError
    from openbb_core.provider.utils.helpers import amake_request
    from pandas import DataFrame, date_range, to_datetime

    new_interval = INTERVAL_MAP.get(interval, interval)

    all_instruments = await get_instruments("all", None)
    all_symbols = {
        d.get("instrument_name"): d.get("creation_timestamp") for d in all_instruments
    }
    creation_date = all_symbols.get(symbol, 0)
    use_start = to_datetime(start_date).timestamp() * 1000 > creation_date

    if creation_date == 0:
        raise ValueError(f"Symbol {symbol} not found")

    def generate_urls(symbol, start_date, end_date, interval, window_size=5000):
        """Generate urls for historical data breaking it down into requests of length window_size."""
        interval_period = f"{interval}min" if interval.lower() != "1d" else "1d"
        interval = "1D" if interval.lower() == "1d" else interval
        dates = date_range(
            start=start_date if use_start else creation_date,
            end=end_date,
            freq=interval_period,
        )
        windows = [
            (dates[i], dates[min(i + window_size, len(dates) - 1)])
            for i in range(0, len(dates), window_size)
        ]
        urls: list = []
        for start, end in windows:
            start_timestamp = int(start.timestamp() * 1000)
            end_timestamp = int(end.timestamp() * 1000)
            url = (
                "https://www.deribit.com/api/v2/public/get_tradingview_chart_data?"
                f"instrument_name={symbol}&start_timestamp={start_timestamp}&"
                f"end_timestamp={end_timestamp}&resolution={interval}"
            )
            urls.append(url)

        return urls

    results: list = []

    async def get_one(url):
        """Get data from one url."""
        json_response = await amake_request(url)
        if json_response.get("error"):  # type: ignore[union-attr]
            raise ValueError(json_response["error"])  # type: ignore[call-overload]
        if json_response.get("result"):  # type: ignore[union-attr]
            result = json_response["result"]  # type: ignore[call-overload]
            df = DataFrame(result)
            df = (
                df.drop(columns=["status"])
                .rename(columns={"ticks": "date", "cost": "volume_notional"})
                .convert_dtypes()
            )
            df["date"] = to_datetime(df.date, unit="ms", origin="unix", utc=True)
            if interval == "1D":
                df.date = df.date.dt.date
            df["symbol"] = symbol
            results.extend(
                df[
                    [
                        "date",
                        "symbol",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "volume_notional",
                    ]
                ].to_dict(orient="records")
            )

    urls = generate_urls(symbol, start_date, end_date, new_interval)

    if len(urls) > 15:
        raise OpenBBError(
            "The request is too large. Break up the request into smaller chunks."
        )

    tasks = [get_one(url) for url in urls]

    await asyncio.gather(*tasks, return_exceptions=True)

    if results:
        return sorted(results, key=lambda x: x["date"])
    raise EmptyDataError("No data found for the given symbol and dates.")


async def check_ohlc_symbol(symbol: str) -> bool | str:
    """
    Check if the symbol has OHLC data.

    Parameters
    ----------
    symbol : str
        The symbol to check.

    Returns
    -------
    bool
        True if the symbol has OHLC data, False otherwise.
    """
    all_instruments = await get_instruments("all", None)
    all_symbols = {
        d.get("instrument_name", ""): d.get("creation_timestamp")
        for d in all_instruments
    }
    all_perpetuals = await get_perpetual_symbols()

    if symbol in all_perpetuals:
        return all_perpetuals.get(symbol, False)
    if symbol in all_symbols:
        return symbol
    return False


async def get_futures_symbols() -> list:
    """
    Get futures symbols.

    Returns
    -------
    list
        A list of futures symbols.
    """
    instruments = await get_instruments("all", "future")
    return [d["instrument_name"] for d in instruments]


async def get_futures_curve_by_hours_ago(symbol, hours):
    """Get futures curve N hours ago."""
    # pylint: disable=import-outside-toplevel
    import asyncio  # noqa
    from datetime import datetime, timedelta

    symbols = await get_futures_curve_symbols(symbol)
    now = datetime.now().replace(microsecond=0, second=0)

    if hours < 24:
        start = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        start = (now - timedelta(hours=hours)).strftime("%Y-%m-%d")
    end = (now + timedelta(days=2)).strftime("%Y-%m-%d")

    results: list = []

    async def get_one(s):
        """Get data for one symbol."""
        data = await get_ohlc_data(s, start, end, "1h")
        result = {
            "instrument_name": data[-1 - hours]["symbol"],
            "hours_ago": hours,
            "last_price": data[-1 - hours]["close"],
        }
        results.append(result)

    tasks = [get_one(s) for s in symbols]

    await asyncio.gather(*tasks, return_exceptions=True)

    return results
