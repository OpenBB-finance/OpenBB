"""Nasdaq Helpers Module."""

from __future__ import annotations

from datetime import date as dateType
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from async_lru import alru_cache

from openbb_nasdaq.utils.constants import BASE_URL, SYMBOL_DIRECTORY_FILES

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pandas import DataFrame

NA_VALUES = {"", "N/A", "NA", "--", "-", "null", "None", "NM"}

CACHE_TTL_DEFAULT = 60 * 15

# How long each endpoint family stays fresh. Reference data changes daily at
# most; statements and filings are quarterly; quotes and movers are the only
# things worth re-fetching within a session.
URL_CACHE_TTL = {
    "*/api/quote/*/info*": 60,
    "*/api/quote/*/summary*": 60,
    "*/api/quote/*/realtime-trades*": 60,
    "*/api/quote/*/extended-trading*": 60,
    "*/api/marketmovers*": 60,
    "*/api/market-info*": 60,
    "*/api/quote/*/option-chain*": 60 * 15,
    "*/api/calendar/*": 60 * 60,
    "*/api/ipo/calendar*": 60 * 60,
    "*/api/news/*": 60 * 30,
    "*/api/quote/*/historical*": 60 * 60 * 6,
    "*/api/quote/*/dividends*": 60 * 60 * 12,
    "*/api/quote/*/short-interest*": 60 * 60 * 12,
    "*/api/analyst/*": 60 * 60 * 12,
    "*/api/company/*/financials*": 60 * 60 * 24,
    "*/api/company/*/earnings-surprise*": 60 * 60 * 24,
    "*/api/company/*/company-profile*": 60 * 60 * 24,
    "*/api/company/*/insider-trades*": 60 * 60 * 6,
    "*/api/company/*/institutional-holdings*": 60 * 60 * 24,
    "*/api/company/*/sec-filings*": 60 * 60 * 6,
    "*/api/screener/*": 60 * 60 * 6,
}

# Nasdaq asset classes, in the order a symbol is probed when the listing
# directory does not identify it.
_PROBE_ORDER = ("stocks", "etf", "index", "mutualfunds", "crypto")


def remove_html_tags(text: str) -> str:
    """Strip HTML tags from a string.

    Parameters
    ----------
    text : str
        The markup to clean.

    Returns
    -------
    str
        The text with tags replaced by spaces.
    """
    import re

    return re.sub(re.compile("<.*?>"), " ", text)


def get_random_agent() -> str:
    """Generate a random user agent for a request.

    Returns
    -------
    str
        A randomly selected browser user-agent string.
    """
    from random_user_agent.user_agent import UserAgent

    return UserAgent(limit=100).get_random_user_agent()


def get_headers(accept_type: str = "json") -> dict:
    """Build the request headers the Nasdaq endpoints require.

    Parameters
    ----------
    accept_type : str
        One of 'json', 'text', or 'pdf'.

    Returns
    -------
    dict
        Headers accepted by api.nasdaq.com.

    Raises
    ------
    ValueError
        If ``accept_type`` is not 'json', 'text', or 'pdf'.
    """
    if accept_type not in ("json", "text", "pdf"):
        raise ValueError("Invalid accept_type. Must be 'json', 'text', or 'pdf'.")

    if accept_type == "pdf":
        return {
            "Accept": "application/pdf,*/*",
            "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
            "User-Agent": get_random_agent(),
            "Connection": "keep-alive",
        }

    if accept_type == "text":
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip",
            "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
            "User-Agent": get_random_agent(),
            "Connection": "keep-alive",
        }

    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Origin": "https://www.nasdaq.com",
        "Referer": "https://www.nasdaq.com/",
        "User-Agent": get_random_agent(),
        "Connection": "keep-alive",
    }


def date_range(start_date, end_date):
    """Yield each date between two dates, inclusive.

    Parameters
    ----------
    start_date : date
        The first date to yield.
    end_date : date
        The last date to yield.

    Yields
    ------
    date
        One date per calendar day in the range.
    """
    from datetime import timedelta

    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


async def _live_request(url: str, **kwargs) -> Any:
    """Fetch a URL without touching the cache."""
    from openbb_core.provider.utils.helpers import amake_request

    return await amake_request(url, headers=get_headers("json"), **kwargs)


async def _cached_request(url: str, **kwargs) -> Any:
    """Fetch a URL through the shared on-disk response cache.

    The session is closed as soon as the response is read. The expensive part
    of the cache is the SQLite backend, which is shared, so a short-lived
    session costs little and leaves nothing open behind it.
    """
    from aiohttp_client_cache.session import CachedSession

    async with CachedSession(cache=get_cache_backend()) as session:
        response = await session.get(url, headers=get_headers("json"), **kwargs)

        try:
            return await response.json(content_type=None)
        finally:
            release = getattr(response, "release", None)

            if callable(release):
                release()


def get_cache_backend():
    """Build the on-disk response cache, with a TTL per endpoint family.

    An options chain's detail fan-out costs one request per strike in the
    fetched expiration, so caching is what keeps a repeat call from re-fetching
    unchanged contracts. TTLs track how often each family actually changes.

    Returns
    -------
    SQLiteBackend
        The shared response cache.
    """
    from aiohttp_client_cache import SQLiteBackend
    from openbb_core.app.utils import get_user_cache_directory

    return SQLiteBackend(
        cache_name=f"{get_user_cache_directory()}/http/nasdaq",
        expire_after=CACHE_TTL_DEFAULT,
        urls_expire_after=URL_CACHE_TTL,
        allowed_codes=(200,),
        allowed_methods=("GET",),
    )


async def get_nasdaq_data(path: str, use_cache: bool = True, **kwargs) -> Any:
    """Request a Nasdaq API path and unwrap the response envelope.

    Parameters
    ----------
    path : str
        The path below ``https://api.nasdaq.com/api``, with any query string.
    use_cache : bool
        When True, responses are served from and written to the on-disk cache
        using the per-endpoint TTLs in ``URL_CACHE_TTL``.

    Returns
    -------
    Any
        The ``data`` member of the response.

    Raises
    ------
    OpenBBError
        If Nasdaq returns a non-200 response code in the envelope.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    url = f"{BASE_URL}/{path.lstrip('/')}"
    response = (
        await _cached_request(url, **kwargs)
        if use_cache
        else await _live_request(url, **kwargs)
    )

    if not isinstance(response, dict):
        raise OpenBBError(f"Unexpected Nasdaq response for '{path}'.")

    status = response.get("status") or {}

    if status.get("rCode") != 200:
        messages = status.get("bCodeMessage") or []
        detail = (
            messages[0].get("errorMessage", "")
            if isinstance(messages, list) and messages
            else ""
        )
        raise OpenBBError(f"Nasdaq request failed for '{path}'. {detail}".strip())

    return response.get("data")


@alru_cache(maxsize=2048)
async def resolve_asset_class(symbol: str) -> str:
    """Work out which Nasdaq asset class a symbol belongs to.

    The listing directory settles stocks versus ETFs without a request. Anything
    it does not carry - indexes, mutual funds, crypto pairs - is probed against
    the quote endpoint and the answer is memoized, so a symbol is resolved at
    most once per process.

    Parameters
    ----------
    symbol : str
        The ticker symbol.

    Returns
    -------
    str
        One of 'stocks', 'etf', 'index', 'mutualfunds', or 'crypto'.
    """
    ticker = symbol.strip().upper()
    listing = _directory_asset_class(ticker)

    if listing is not None:
        return listing

    for asset_class in _PROBE_ORDER:
        try:
            await get_nasdaq_data(f"quote/{ticker}/info?assetclass={asset_class}")
        except Exception:  # noqa: BLE001, S112
            continue

        return asset_class

    return "stocks"


@lru_cache(maxsize=1)
def _directory_index() -> dict:
    """Index the Nasdaq listing directory by symbol, mapping to its asset class.

    Returns
    -------
    dict
        Symbol mapped to 'stocks' or 'etf'. Empty when the file is unreachable.
    """
    try:
        directory = parse_directory(get_nasdaq_directory("nasdaqtraded"))
    except Exception:  # noqa: BLE001
        return {}

    symbols = directory.get("Symbol")
    etfs = directory.get("ETF")

    if symbols is None:
        return {}

    if etfs is None:
        return {str(s).upper(): "stocks" for s in symbols}

    return {
        str(s).upper(): ("etf" if str(e).strip() == "Y" else "stocks")
        for s, e in zip(symbols, etfs)
    }


def _directory_asset_class(symbol: str) -> str | None:
    """Look a symbol up in the listing directory.

    Parameters
    ----------
    symbol : str
        The upper-cased ticker symbol.

    Returns
    -------
    str | None
        'stocks' or 'etf', or None when the directory does not carry the symbol.
    """
    return _directory_index().get(symbol)


def clean_value(value: Any) -> Any:
    """Normalize a Nasdaq display string to a plain value.

    Strips currency symbols, thousands separators, percent signs, and the
    various placeholders Nasdaq uses for a missing value. Parenthesized
    numbers are returned as negatives.

    Parameters
    ----------
    value : Any
        The raw cell value.

    Returns
    -------
    Any
        None for placeholders, otherwise the cleaned string.
    """
    if value is None or not isinstance(value, str):
        return value

    cleaned = value.strip()

    if cleaned in NA_VALUES:
        return None

    cleaned = cleaned.replace("$", "").replace(",", "").replace("%", "").strip()

    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"

    return cleaned or None


def to_number(value: Any) -> float | None:
    """Coerce a Nasdaq display string to a float.

    Parameters
    ----------
    value : Any
        The raw cell value.

    Returns
    -------
    float | None
        The number, or None when the cell carries no value.
    """
    cleaned = clean_value(value)

    if cleaned is None:
        return None

    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return None


def to_percent(value: Any) -> float | None:
    """Coerce a Nasdaq percentage string to a normalized fraction.

    Parameters
    ----------
    value : Any
        The raw cell value - i.e., '+3.53%'.

    Returns
    -------
    float | None
        The value divided by 100, or None when the cell carries no value.
    """
    number = to_number(value)

    return None if number is None else number / 100


def to_date(value: Any) -> dateType | None:
    """Coerce a Nasdaq date string to a date.

    Parameters
    ----------
    value : Any
        The raw cell value, in any of the formats Nasdaq emits.

    Returns
    -------
    date | None
        The parsed date, or None when the cell carries no value.
    """
    from dateutil import parser

    cleaned = value.strip() if isinstance(value, str) else value

    if not cleaned or (isinstance(cleaned, str) and cleaned in NA_VALUES):
        return None

    if isinstance(cleaned, dateType):
        return cleaned

    try:
        return parser.parse(str(cleaned)).date()
    except (TypeError, ValueError, OverflowError):
        return None


@lru_cache(maxsize=4)
def get_nasdaq_directory(listing: str = "nasdaqtraded") -> str:
    """Get a Nasdaq symbol directory file over HTTPS.

    Parameters
    ----------
    listing : str
        One of 'nasdaqtraded', 'nasdaqlisted', or 'otherlisted'.

    Returns
    -------
    str
        The pipe-delimited directory file.

    Raises
    ------
    OpenBBError
        If the file cannot be retrieved.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    url = f"{SYMBOL_DIRECTORY_FILES}/{listing}.txt"

    try:
        response = make_request(url, headers={"User-Agent": get_random_agent()})
        response.raise_for_status()
    except Exception as exc:
        raise OpenBBError(
            f"Failed to download the Nasdaq {listing} directory."
        ) from exc

    return response.text


def parse_directory(content: str) -> DataFrame:
    """Parse a pipe-delimited Nasdaq directory file.

    Parameters
    ----------
    content : str
        The raw directory file.

    Returns
    -------
    DataFrame
        The directory rows, with the trailing file-creation line removed.
    """
    from io import StringIO

    from pandas import read_csv

    directory = read_csv(StringIO(content), sep="|")

    return directory[~directory.iloc[:, 0].astype(str).str.startswith("File Creation")]


async def get_historical_prices(
    symbol: str,
    asset_class: str,
    start_date: Any = None,
    end_date: Any = None,
    limit: int = 10000,
) -> list[dict]:
    """Get the daily OHLCV history for any Nasdaq-quoted symbol.

    Parameters
    ----------
    symbol : str
        The ticker symbol.
    asset_class : str
        One of 'stocks', 'etf', 'index', 'crypto', or 'mutualfunds'.
    start_date : date | None
        The first session to return.
    end_date : date | None
        The last session to return.
    limit : int
        The maximum number of sessions to request.

    Returns
    -------
    list[dict]
        One record per session, with numeric OHLCV values.

    Raises
    ------
    EmptyDataError
        If Nasdaq publishes no history for the symbol.
    """
    from datetime import date, timedelta

    from openbb_core.provider.utils.errors import EmptyDataError

    end = end_date or date.today()
    start = start_date or (end - timedelta(days=365))
    path = (
        f"quote/{symbol.upper()}/historical?assetclass={asset_class}"
        f"&fromdate={start}&todate={end}&limit={limit}"
    )
    data = await get_nasdaq_data(path)
    rows = rows_from_table((data or {}).get("tradesTable"))

    if not rows:
        raise EmptyDataError(f"No historical prices were found for {symbol}.")

    results: list[dict] = []

    for row in rows:
        session = to_date(row.get("date"))

        if session is None:
            continue

        results.append(
            {
                "date": session,
                "open": to_number(row.get("open")),
                "high": to_number(row.get("high")),
                "low": to_number(row.get("low")),
                "close": to_number(row.get("close")),
                "volume": to_number(row.get("volume")),
            }
        )

    return sorted(results, key=lambda r: r["date"])


async def gather_historical_prices(
    symbols: str,
    asset_class: str | None = None,
    start_date: Any = None,
    end_date: Any = None,
) -> list[dict]:
    """Get the daily history for one or more comma-separated symbols.

    The ``symbol`` column is only added when more than one symbol is requested,
    matching the OpenBB convention for multi-symbol price endpoints.

    Parameters
    ----------
    symbols : str
        One or more comma-separated ticker symbols.
    asset_class : str | None
        One of 'stocks', 'etf', 'index', 'crypto', or 'mutualfunds'. Resolved
        from each symbol when omitted.
    start_date : date | None
        The first session to return.
    end_date : date | None
        The last session to return.

    Returns
    -------
    list[dict]
        Session records, sorted by date and then symbol.

    Raises
    ------
    EmptyDataError
        If none of the requested symbols returned any history.
    """
    import asyncio
    from warnings import warn

    from openbb_core.provider.utils.errors import EmptyDataError

    tickers = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    results: list[dict] = []

    async def get_one(ticker: str) -> None:
        """Collect one symbol's history, warning when it is unavailable."""
        try:
            rows = await get_historical_prices(
                ticker,
                asset_class or await resolve_asset_class(ticker),
                start_date,
                end_date,
            )
        except Exception as exc:  # noqa: BLE001
            warn(f"No historical prices were returned for {ticker}. {exc}")
            return

        if len(tickers) > 1:
            for row in rows:
                row["symbol"] = ticker

        results.extend(rows)

    await asyncio.gather(*[get_one(ticker) for ticker in tickers])

    if not results:
        raise EmptyDataError("No historical prices were returned for any symbol.")

    return sorted(results, key=lambda r: (r["date"], r.get("symbol") or ""))


async def get_basic_quotes(symbols: Sequence[str]) -> list[dict]:
    """Get a light quote for many symbols in a single request.

    The asset class of every symbol is resolved first, because the endpoint
    keys each record by a ``SYMBOL|ASSETCLASS`` pair. Mixed asset classes are
    served together, which is what makes one request enough for a watchlist.

    Parameters
    ----------
    symbols : Sequence[str]
        The ticker symbols.

    Returns
    -------
    list[dict]
        One record per symbol, in the requested order.

    Raises
    ------
    EmptyDataError
        If no symbol returned a quote.
    """
    import asyncio

    from openbb_core.provider.utils.errors import EmptyDataError

    tickers = [s.strip().upper() for s in symbols if s and s.strip()]
    asset_classes = await asyncio.gather(
        *[resolve_asset_class(ticker) for ticker in tickers]
    )
    query = "&".join(
        f"symbol={ticker.lower()}%7C{asset_class}"
        for ticker, asset_class in zip(tickers, asset_classes)
    )
    data = await get_nasdaq_data(f"quote/basic?{query}")
    records = (data or {}).get("records") or []
    by_symbol = {
        str(record.get("key", "")).split("|", 1)[0].upper(): record
        for record in records
    }
    results = [by_symbol[ticker] for ticker in tickers if ticker in by_symbol]

    if not results:
        raise EmptyDataError("No quotes were returned for any symbol.")

    return results


def rows_from_table(table: Any) -> list[dict]:
    """Return the row list from any of the Nasdaq table envelopes.

    Nasdaq nests rows under ``table.rows``, ``rows``, or ``table.table.rows``
    depending on the endpoint.

    Parameters
    ----------
    table : Any
        The table object from a Nasdaq response.

    Returns
    -------
    list[dict]
        The rows, or an empty list when none are present.
    """
    if not isinstance(table, dict):
        return []

    if isinstance(table.get("rows"), list):
        return table["rows"]

    nested = table.get("table")

    if isinstance(nested, dict) and isinstance(nested.get("rows"), list):
        return nested["rows"]

    return []


@alru_cache(maxsize=1)
async def get_symbol_choices() -> list[dict]:
    """Get ``[{label, value}]`` choices for the Nasdaq-traded operating companies.

    Test issues, ETFs, and the non-common share classes Nasdaq carries in the
    directory are excluded so the picker only offers filing entities.

    Returns
    -------
    list[dict]
        Label/value pairs suitable for an OpenBB Workspace dropdown.
    """
    from openbb_nasdaq.models.equity_search import NasdaqEquitySearchFetcher

    directory = await NasdaqEquitySearchFetcher.fetch_data({}, {})
    excluded = ("%", "Unit", "Rights", "Warrant", "Preferred")
    choices: list[dict] = []

    for item in directory:
        row = item.model_dump()  # ty: ignore[unresolved-attribute]
        name = row.get("name") or ""

        if row.get("test_issue") == "Y" or row.get("etf") == "Y":
            continue

        if any(token in name for token in excluded):
            continue

        choices.append(
            {
                "value": row["symbol"],
                "label": row["symbol"],
                "extraInfo": {"description": name},
            }
        )

    return choices


@alru_cache(maxsize=1)
async def get_index_symbol_choices() -> list[dict]:
    """Get ``[{label, value}]`` choices for the Nasdaq-calculated index universe.

    Returns
    -------
    list[dict]
        Label/value pairs suitable for an OpenBB Workspace dropdown.
    """
    from openbb_nasdaq.models.index_search import NasdaqIndexSearchFetcher

    directory = await NasdaqIndexSearchFetcher.fetch_data({}, {})
    choices: list[dict] = []

    for item in directory:
        row = item.model_dump()  # ty: ignore[unresolved-attribute]

        if not row.get("symbol"):
            continue

        choices.append(
            {
                "value": row["symbol"],
                "label": row["symbol"],
                "extraInfo": {"description": row.get("name") or ""},
            }
        )

    return choices


@alru_cache(maxsize=1)
async def get_etf_symbol_choices() -> list[dict]:
    """Get ``[{label, value}]`` choices for the Nasdaq-traded fund universe.

    Returns
    -------
    list[dict]
        Label/value pairs suitable for an OpenBB Workspace dropdown.
    """
    from openbb_nasdaq.models.etf_search import NasdaqEtfSearchFetcher

    directory = await NasdaqEtfSearchFetcher.fetch_data({}, {})
    choices: list[dict] = []

    for item in directory:
        row = item.model_dump()  # ty: ignore[unresolved-attribute]

        if not row.get("symbol"):
            continue

        choices.append(
            {
                "value": row["symbol"],
                "label": row["symbol"],
                "extraInfo": {"description": row.get("name") or ""},
            }
        )

    return choices


@alru_cache(maxsize=128)
async def get_document_choices(
    symbol: str | None = None,
    year: int | None = None,
    form_group: str = "8k",
) -> list[dict]:
    """Get ``[{label, value}]`` choices of filing PDFs for a symbol.

    Parameters
    ----------
    symbol : str | None
        The ticker symbol.
    year : int | None
        The calendar year of the filings.
    form_group : str
        The SEC form group.

    Returns
    -------
    list[dict]
        Label/value pairs where the value is the PDF URL.
    """
    from openbb_nasdaq.models.company_filings import NasdaqCompanyFilingsFetcher

    if not symbol:
        return []

    try:
        items = await NasdaqCompanyFilingsFetcher.fetch_data(
            {"symbol": symbol, "year": year, "form_group": form_group}, {}
        )
    except Exception:  # noqa: BLE001
        return []

    label = "8-K" if form_group == "8k" else form_group.title()
    choices: list[dict] = []

    for item in items:
        form = item.model_dump()  # ty: ignore[unresolved-attribute]
        url = form.get("pdf_url")

        if not url:
            continue

        choices.append(
            {"label": f"{form.get('filing_date', '')} - {label}", "value": url}
        )

    return choices


@alru_cache(maxsize=128)
async def download_filing_pdf(document_url: str) -> str:
    """Download a filing PDF and return it base64-encoded.

    Parameters
    ----------
    document_url : str
        The fully-qualified PDF URL.

    Returns
    -------
    str
        The base64-encoded document.
    """
    import base64

    from openbb_core.provider.utils.helpers import amake_request

    async def _read(response, _):
        """Return the raw response body."""
        return await response.read()

    content = await amake_request(
        document_url, headers=get_headers("text"), response_callback=_read
    )

    return base64.b64encode(content).decode("utf-8")  # ty: ignore[invalid-argument-type]


async def open_filing_document(document_url: str) -> dict:
    """Open one filing PDF for the Workspace multi-file viewer.

    Parameters
    ----------
    document_url : str
        The fully-qualified PDF URL.

    Returns
    -------
    dict
        Either the encoded document with its filename, or an error payload.
    """
    try:
        encoded = await download_filing_pdf(document_url)
    except Exception as exc:  # noqa: BLE001
        return {
            "error_type": "download_error",
            "content": f"Error fetching document: {exc}",
        }

    return {
        "content": encoded,
        "data_format": {"data_type": "pdf", "filename": _filing_filename(document_url)},
    }


def _filing_filename(document_url: str) -> str:
    """Build a readable filename from a Nasdaq filing URL.

    Parameters
    ----------
    document_url : str
        The fully-qualified PDF URL.

    Returns
    -------
    str
        A '{symbol}-{date}-{form}.pdf' filename, or a generic fallback.
    """
    from urllib.parse import parse_qs, urlparse

    params = parse_qs(urlparse(document_url).query)
    symbol = (params.get("symbol") or [""])[0]
    form_type = (params.get("formType") or [""])[0].replace("-", "")
    filed = (params.get("dateFiled") or [""])[0][:10].replace("-", "")

    if not symbol:
        return "filing.pdf"

    return f"{symbol}-{filed}-{form_type}.pdf"


DETAIL_FIELDS = {
    "last_trade_price": "LastSale",
    "change": "Net",
    "high": "DayHigh",
    "low": "DayLow",
    "volume": "Volume",
    "prev_close": "PrevClose",
    "open": "Open",
    "open_interest": "OpenInterest",
    "tick": "Tick",
    "bid": "Bid",
    "ask": "Ask",
    "bid_size": "BidSize",
    "ask_size": "AskSize",
    "contract_high": "ContractHigh",
    "contract_low": "ContractLow",
    "exchange": "Market",
}

GREEK_FIELDS = {
    "delta": "Delta",
    "gamma": "Gamma",
    "rho": "Rho",
    "theta": "Theta",
    "vega": "Vega",
    "implied_volatility": "Impvol",
}

TEXT_FIELDS = {"tick", "exchange"}


def build_record_id(
    symbol: str, expiration: dateType, strike: float, option_type: str
) -> str:
    """Build the Nasdaq recordID for one option contract.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    expiration : date
        The contract expiration date.
    strike : float
        The contract strike price.
    option_type : str
        Either 'call' or 'put'.

    Returns
    -------
    str
        The recordID - i.e., 'NVDA--260807C00187500'.
    """
    side = "C" if option_type == "call" else "P"
    strike_part = f"{int(round(strike * 1000)):08d}"

    return f"{symbol.upper()}--{expiration:%y%m%d}{side}{strike_part}"


async def get_contract_detail(
    symbol: str,
    expiration: Any,
    strike: float,
    asset_class: str = "stocks",
) -> dict:
    """Get the full per-contract detail and greeks for one strike.

    Nasdaq's chain endpoint carries only last/change/bid/ask/volume/open-interest,
    and its greeks endpoint is locked to the front expiration. The contract
    endpoint returns both sides of a strike with the full quote detail and the
    greeks, for any expiration.

    Parameters
    ----------
    symbol : str
        The underlying ticker symbol.
    expiration : date
        The contract expiration date.
    strike : float
        The contract strike price.
    asset_class : str
        One of 'stocks', 'etf', or 'index'.

    Returns
    -------
    dict
        Mapping of 'call' and 'put' to that side's fields.
    """
    record_id = build_record_id(symbol, expiration, strike, "call")
    payload = await get_nasdaq_data(
        f"quote/{symbol.lower()}/option-chain"
        f"?assetclass={asset_class}&recordID={record_id}"
    )
    sides: dict = {}

    for side, key in (("call", "optionChainCallData"), ("put", "optionChainPutData")):
        block = (payload or {}).get(key) or {}
        detail = block.get("optionChainListData") or {}

        if not detail:
            continue

        fields: dict = {}

        for field, label in DETAIL_FIELDS.items():
            raw = (detail.get(label) or {}).get("value")
            fields[field] = raw if field in TEXT_FIELDS else to_number(raw)

        greeks = block.get("optionChainGreeksList") or {}

        for field, label in GREEK_FIELDS.items():
            fields[field] = to_number((greeks.get(label) or {}).get("value"))

        sides[side] = fields

    return sides
