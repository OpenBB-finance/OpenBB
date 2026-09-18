"""The cross-market instrument directory, swept from the QuoteMedia symbology."""

from typing import TYPE_CHECKING, Any

from openbb_tmx.utils.memo import memoize

if TYPE_CHECKING:
    from collections.abc import Sequence

LOOKUP_TOOL = "InteractiveChart"

PHRASE_PAGE = 2000

DIRECTORY_TTL = 60 * 60 * 24
ROW_CAP = 20000
PREFIX_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
SWEEP_CONCURRENCY = 6
MAX_PREFIX_LENGTH = 3

SYMBOL_TYPES = (
    "Equity",
    "ETF",
    "Mutual Fund",
    "Money Market Fund",
    "Index",
    "Future",
    "Forex",
    "Crypto",
)


async def lookup_symbols(
    query: str,
    limit: int = 100,
    country: str | None = None,
    symbol_only: bool = False,
    use_cache: bool = True,
) -> list[dict]:
    """Search the QuoteMedia symbology.

    Parameters
    ----------
    query : str
        The symbol or name fragment to match.
    limit : int
        The maximum number of rows to return.
    country : str or None
        Restrict to a two-letter country code, such as 'CA'.
    symbol_only : bool
        Match the symbol only, instead of the symbol or the name.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per matching instrument.
    """
    from urllib.parse import urlencode

    from openbb_tmx.utils.cache import amake_request
    from openbb_tmx.utils.quotemedia import APP_URL, get_token

    if not query:
        return []

    token = await get_token(LOOKUP_TOOL)
    params: dict[str, Any] = {"q": query, "limit": limit, "token": token}

    if country:
        params["countryCode"] = country

    if symbol_only:
        params["searchType"] = "symbol"

    url = f"{APP_URL}/datatool/lookup.json?{urlencode(params)}"

    for attempt in range(2):
        try:
            response = await amake_request(url, use_cache=use_cache)
        except Exception:
            response = None

        if isinstance(response, list):
            if response or " " not in query.strip():
                return response

            return await _lookup_phrase(query, limit, country, symbol_only, use_cache)

        if attempt == 0:
            get_token.cache_clear()
            params["token"] = await get_token(LOOKUP_TOOL)
            url = f"{APP_URL}/datatool/lookup.json?{urlencode(params)}"

    return []


async def _lookup_phrase(
    query: str,
    limit: int,
    country: str | None,
    symbol_only: bool,
    use_cache: bool,
) -> list[dict]:
    """Match a multi-word query the symbology cannot answer directly.

    Parameters
    ----------
    query : str
        The phrase to match.
    limit : int
        The maximum number of rows to return.
    country : str or None
        Restrict to a two-letter country code.
    symbol_only : bool
        Match the symbol only, instead of the symbol or the name.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        The rows whose name contains every word of the phrase.
    """
    words = [w for w in query.strip().split() if w]

    if not words:
        return []

    import asyncio

    pages = await asyncio.gather(
        *(
            lookup_symbols(
                word,
                limit=max(limit, PHRASE_PAGE),
                country=country,
                symbol_only=symbol_only,
                use_cache=use_cache,
            )
            for word in words
        )
    )
    rows = list({row.get("symbol"): row for page in pages for row in page}.values())
    needles = [w.casefold() for w in words]
    matched = [
        row
        for row in rows
        if all(
            n in f"{row.get('name') or ''} {row.get('symbol') or ''}".casefold()
            for n in needles
        )
    ]

    return matched[:limit]


async def _sweep_prefix(
    prefix: str, country: str | None, results: dict, use_cache: bool
) -> None:
    """Sweep one prefix, recursing when the row cap truncates the result."""
    rows = await lookup_symbols(
        prefix,
        limit=ROW_CAP,
        country=country,
        symbol_only=True,
        use_cache=use_cache,
    )

    for row in rows:
        symbol_id = row.get("symbolId")

        if symbol_id is not None:
            results[symbol_id] = row

    if len(rows) < ROW_CAP or len(prefix) >= MAX_PREFIX_LENGTH:
        return

    for char in PREFIX_ALPHABET:
        await _sweep_prefix(prefix + char, country, results, use_cache)


@memoize(ttl=DIRECTORY_TTL)
async def get_master_directory(
    country: str | None = "CA", use_cache: bool = True
) -> tuple[dict, ...]:
    """Sweep the complete instrument directory for a country.

    Parameters
    ----------
    country : str or None
        The two-letter country code, or None for every market.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    tuple[dict, ...]
        Every instrument, keyed uniquely by its QuoteMedia symbol id.

    Raises
    ------
    OpenBBError
        If the directory comes back empty.
    """
    import asyncio

    from openbb_core.app.model.abstract.error import OpenBBError

    results: dict = {}
    semaphore = asyncio.Semaphore(SWEEP_CONCURRENCY)

    async def worker(prefix: str) -> None:
        async with semaphore:
            await _sweep_prefix(prefix, country, results, use_cache)

    await asyncio.gather(*(worker(char) for char in PREFIX_ALPHABET))

    if not results:
        raise OpenBBError("The TMX instrument directory came back empty.")

    return tuple(results.values())


async def browse_symbols(
    limit: int = 200,
    country: str | None = "CA",
    symbol_types: "Sequence[str] | None" = None,
    use_cache: bool = True,
) -> list[dict]:
    """List the directory, largest first, for a search with nothing to match on.

    Parameters
    ----------
    limit : int
        The maximum number of instruments to return.
    country : str or None
        The two-letter country code, or None for every market.
    symbol_types : Sequence[str] or None
        Restrict to these instrument types.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per instrument, primary listings only.
    """
    frame = await get_directory_frame(
        country=country, symbol_types=symbol_types, use_cache=use_cache
    )

    if frame.empty:
        return []

    primary = frame[~frame["symbol"].astype(str).str.contains(":")]
    ranked = primary.sort_values("marketCap", ascending=False)

    return ranked.head(limit).to_dict(orient="records")


async def get_directory_frame(
    country: str | None = "CA",
    symbol_types: "Sequence[str] | None" = None,
    exchanges: "Sequence[str] | None" = None,
    use_cache: bool = True,
):
    """Return the instrument directory as a filtered DataFrame.

    Parameters
    ----------
    country : str or None
        The two-letter country code, or None for every market.
    symbol_types : Sequence[str] or None
        Restrict to these instrument types.
    exchanges : Sequence[str] or None
        Restrict to these exchange short names.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    DataFrame
        The filtered directory.
    """
    from pandas import DataFrame

    records = await get_master_directory(country=country, use_cache=use_cache)
    frame = DataFrame(list(records))

    if symbol_types:
        frame = frame[frame["symbolType"].isin(list(symbol_types))]

    if exchanges:
        frame = frame[frame["exchangeShortName"].isin(list(exchanges))]

    return frame.reset_index(drop=True)
