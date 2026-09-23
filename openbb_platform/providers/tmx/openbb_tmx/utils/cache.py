"""TMX shared response cache and HTTP transport."""

import logging
from contextlib import suppress
from typing import TYPE_CHECKING, Any

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from aiohttp_client_cache import SQLiteBackend

CACHE_TTL_DEFAULT = 60 * 15
CACHE_MAX_BYTES = 256 * 1024 * 1024
CACHE_SWEEP_PASSES = 3
CACHE_BUSY_TIMEOUT = 30.0

INCREMENTAL = 2

IGNORED_PARAMS = ("token",)

MINUTE = 60
HOUR = 60 * 60
DAY = 60 * 60 * 24

URL_CACHE_TTL = {
    "*www.tsx.com/json/company-directory/search*": 2 * DAY,
    "*dgr53wu9i7rmp.cloudfront.net/etfs/etfs.json": 4 * HOUR,
    "*tmxinfoservices.com/files/indices/*": DAY,
    "*bondtradedata.ciro.ca/debtip/*": DAY,
    "*m-x.ca/en/trading/data/options-list*": DAY,
    "*m-x.ca/en/resources/education/covered-call-screener*": 15 * MINUTE,
    "*m-x.ca/f_publications_en/*": DAY,
    "*m-x.ca/en/trading/data/quotes*": 15 * MINUTE,
    "*m-x.ca/en/trading/data/historical*": 6 * HOUR,
    "*m-x.ca/en/trading/data/intra-session-summary*": 5 * MINUTE,
    "*m-x.ca/en/trading/data/daily-special-terms-transactions*": 15 * MINUTE,
    "*m-x.ca/en/trading/data/monthly-volumes-and-open-interest*": DAY,
    "*m-x.ca/en/trading/data/market-records*": DAY,
    "*m-x.ca/files/options-summary-en.xlsx": 6 * HOUR,
    "*m-x.ca/files/ratio-*.csv": 6 * HOUR,
    "*www.tsx.com/files/trading/*": 15 * MINUTE,
    "*www.tsx.com/files/alpha/*": 15 * MINUTE,
    "*www.tsx.com/en/trading/calendars-and-trading-hours*": 7 * DAY,
    "*www.tsx.com/en/trading/market-data-and-statistics*": 15 * MINUTE,
    "*app.quotemedia.com/datatool/getQuotes*": MINUTE,
    "*app.quotemedia.com/datatool/getOptionQuotes*": 15 * MINUTE,
    "*app.quotemedia.com/datatool/getFinancials*": DAY,
    "*app.quotemedia.com/datatool/getEnhancedQuotes*": 6 * HOUR,
}

GQL_TTL = {
    "getQuoteBySymbol": MINUTE,
    "getQuoteForSymbols": MINUTE,
    "getTrendingQuotes": MINUTE,
    "getMarketMovers": MINUTE,
    "getMarketSummary": MINUTE,
    "getCompanyMostRecentTrades": MINUTE,
    "getCompanyPriceHistory": 6 * HOUR,
    "getTimeSeriesData": 6 * HOUR,
    "getCompanyFilings": 6 * HOUR,
    "getCompanyInsidersActivities": 6 * HOUR,
    "getInsiderTransactions": 6 * HOUR,
    "GetCompanyShortInterest": 12 * HOUR,
    "getDividendsForSymbol": 12 * HOUR,
    "getSplitsForSymbol": 12 * HOUR,
    "getCompanyAnalysts": 12 * HOUR,
    "getEnhancedEarningsForDate": 6 * HOUR,
    "getNewsForSymbol": 30 * MINUTE,
    "getNewsForSymbols": 30 * MINUTE,
    "getIndexConstituents": DAY,
    "getIndexKeyData": DAY,
    "getETFs": 4 * HOUR,
    "findTmxCompaniesByKeywords": DAY,
    "getStockListSymbolsWithQuote": HOUR,
    "getTsx30Companies": 7 * DAY,
    "getVenture50Companies": 7 * DAY,
}

GQL_URL = "https://app-money.tmx.com/graphql"


def get_random_agent() -> str:
    """Generate a random user agent for a request.

    Returns
    -------
    str
        A randomly selected browser user-agent string.
    """
    from random_user_agent.user_agent import UserAgent

    return UserAgent(limit=100).get_random_user_agent()


def get_headers(
    accept_type: str = "json", referer: str = "https://money.tmx.com/"
) -> dict:
    """Build request headers for the TMX endpoints.

    Parameters
    ----------
    accept_type : str
        One of 'json', 'text', or 'binary'.
    referer : str
        The referer to send.

    Returns
    -------
    dict
        Headers accepted by the TMX hosts.

    Raises
    ------
    ValueError
        If ``accept_type`` is not 'json', 'text', or 'binary'.
    """
    if accept_type not in ("json", "text", "binary"):
        raise ValueError("Invalid accept_type. Must be 'json', 'text', or 'binary'.")

    accept = {
        "json": "application/json, text/plain, */*",
        "text": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "binary": "*/*",
    }[accept_type]

    return {
        "Accept": accept,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Origin": referer.rstrip("/"),
        "Referer": referer,
        "User-Agent": get_random_agent(),
        "Connection": "keep-alive",
    }


_swept = False


def cache_path() -> str:
    """Return the file the cached responses are kept in."""
    from openbb_core.app.utils import get_user_cache_directory

    return f"{get_user_cache_directory()}/http/tmx"


def prepare_database() -> None:
    """Set the cache file to write-ahead logging and incremental vacuuming."""
    import sqlite3
    from pathlib import Path

    stored = Path(f"{cache_path()}.sqlite")
    stored.parent.mkdir(parents=True, exist_ok=True)

    with suppress(sqlite3.Error):
        connection = sqlite3.connect(stored, timeout=CACHE_BUSY_TIMEOUT)

        try:
            connection.execute("PRAGMA journal_mode=WAL")

            if connection.execute("PRAGMA auto_vacuum").fetchone()[0] != INCREMENTAL:
                connection.execute("PRAGMA auto_vacuum=INCREMENTAL")
                connection.execute("VACUUM")

            connection.commit()
        finally:
            connection.close()


def get_cache_backend() -> "SQLiteBackend":
    """Build the on-disk response cache, with a TTL per endpoint family.

    Returns
    -------
    SQLiteBackend
        The shared response cache.
    """
    from aiohttp_client_cache import SQLiteBackend

    prepare_database()

    return SQLiteBackend(
        cache_name=cache_path(),
        expire_after=CACHE_TTL_DEFAULT,
        urls_expire_after=URL_CACHE_TTL,
        allowed_codes=(200,),
        allowed_methods=("GET", "POST"),
        include_headers=False,
        ignored_params=IGNORED_PARAMS,
        timeout=CACHE_BUSY_TIMEOUT,
        fast_save=True,
    )


async def _oldest(backend: "SQLiteBackend", count: int) -> set:
    """Return the keys of the entries written longest ago."""
    keys: set = set()

    async for key in backend.responses.keys():
        keys.add(key)

        if len(keys) >= count:
            break

    return keys


async def _vacuum(backend: "SQLiteBackend") -> None:
    """Give back the pages the deleted responses were held in."""
    from aiohttp_client_cache.backends.sqlite import SQLiteCache

    stored = backend.responses

    if not isinstance(stored, SQLiteCache):
        return

    async with stored.get_connection(commit=True) as connection:
        await connection.execute("PRAGMA incremental_vacuum")
        await connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")


async def sweep_cache(backend: "SQLiteBackend") -> None:
    """Drop what has expired, then the oldest of what is left if still too big.

    Parameters
    ----------
    backend : SQLiteBackend
        The cache to sweep.
    """
    from pathlib import Path

    global _swept  # noqa: PLW0603

    if _swept:
        return

    _swept = True
    await backend.delete_expired_responses()
    await _vacuum(backend)
    stored = Path(f"{cache_path()}.sqlite")

    for _ in range(CACHE_SWEEP_PASSES):
        if not stored.exists() or stored.stat().st_size <= CACHE_MAX_BYTES:
            return

        held = await backend.responses.size()
        overshoot = 1 - CACHE_MAX_BYTES / stored.stat().st_size
        dropped = await _oldest(backend, max(1, round(held * overshoot)))

        if not dropped:
            return

        await backend.responses.bulk_delete(dropped)
        await _vacuum(backend)


async def _read(response, accept_type: str) -> Any:
    """Read a response body according to the accept type."""
    if accept_type == "json":
        return await response.json(content_type=None)

    if accept_type == "text":
        return await response.text()

    return await response.read()


def _release(response) -> None:
    """Release a response, tolerating cached responses that cannot be."""
    release = getattr(response, "release", None)

    if callable(release):
        release()


async def _uncached_on_cache_error(send, use_cache: bool):
    """Send a request, falling back to the plain session if the cache fails.

    Parameters
    ----------
    send : Callable
        Takes whether to use the cache, and returns the response.
    use_cache : bool
        Whether to try the cache at all.

    Returns
    -------
    Any
        The response, however it was obtained.
    """
    import sqlite3

    if not use_cache:
        return await send(False)

    try:
        return await send(True)
    except sqlite3.Error:
        _logger.warning("The TMX response cache is unavailable; bypassing it.")

        return await send(False)


async def amake_request(
    url: str,
    *,
    use_cache: bool = True,
    accept_type: str = "json",
    referer: str = "https://money.tmx.com/",
    headers: dict | None = None,
    method: str = "GET",
    **kwargs: Any,
) -> Any:
    """Fetch a URL, through the shared on-disk cache by default.

    Parameters
    ----------
    url : str
        The URL to fetch.
    use_cache : bool
        Whether to read and write the on-disk cache.
    accept_type : str
        One of 'json', 'text', or 'binary'.
    referer : str
        The referer to send.
    headers : dict or None
        Headers to send instead of the defaults.
    method : str
        The HTTP method. A form-posted page is cached the same way a fetched
        one is, keyed on its body.

    Returns
    -------
    Any
        The decoded response body.
    """
    from openbb_tmx.utils.session import get_cached_session, get_session

    request_headers = headers or get_headers(accept_type, referer)
    kwargs.setdefault("timeout", 120)

    async def _send(cached: bool):
        """Send the request through the cached or the plain session."""
        session = await get_cached_session() if cached else await get_session()

        return await session.request(method, url, headers=request_headers, **kwargs)

    response = await _uncached_on_cache_error(_send, use_cache)

    try:
        return await _read(response, accept_type)
    finally:
        _release(response)


async def amake_gql_request(
    operation: str,
    query: str,
    variables: dict | None = None,
    symbol: str | None = None,
    use_cache: bool = True,
    **kwargs: Any,
) -> Any:
    """Post a GraphQL operation to the TMX money API.

    Parameters
    ----------
    operation : str
        The operation name, which also selects the cache TTL.
    query : str
        The GraphQL query document.
    variables : dict or None
        The query variables.
    symbol : str or None
        The symbol the request is for, used to build the referer.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    Any
        The ``data`` member of the GraphQL response.

    Raises
    ------
    OpenBBError
        If the response carries GraphQL errors.
    """
    import json

    from openbb_core.app.model.abstract.error import OpenBBError

    referer = (
        f"https://money.tmx.com/en/quote/{symbol}"
        if symbol
        else "https://money.tmx.com/"
    )
    headers = {
        "authority": "app-money.tmx.com",
        "Accept": "*/*",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/json",
        "locale": "en",
        "Origin": "https://money.tmx.com",
        "Referer": referer,
        "User-Agent": get_random_agent(),
    }
    payload = json.dumps(
        {"operationName": operation, "variables": variables or {}, "query": query}
    )
    kwargs.setdefault("timeout", 120)

    from openbb_tmx.utils.session import get_cached_session, get_session

    async def _post(session, **extra) -> Any:
        response = await session.post(
            GQL_URL, data=payload, headers=headers, **extra, **kwargs
        )

        try:
            return await response.json(content_type=None)
        finally:
            _release(response)

    async def _send(cached: bool) -> Any:
        """Post through the cached or the plain session."""
        if cached:
            return await _post(
                await get_cached_session(),
                expire_after=GQL_TTL.get(operation, CACHE_TTL_DEFAULT),
            )

        return await _post(await get_session())

    result = await _uncached_on_cache_error(_send, use_cache)

    if not isinstance(result, dict):
        raise OpenBBError(f"Unexpected TMX response for {operation}.")

    if result.get("errors"):
        messages = "; ".join(
            error.get("message", "") for error in result["errors"] if error
        )
        raise OpenBBError(f"TMX GraphQL error for {operation} -> {messages}")

    return result.get("data")
