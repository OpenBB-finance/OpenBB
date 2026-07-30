"""Cboe Helpers."""

from __future__ import annotations

import logging
from datetime import (
    date as dateType,
    datetime,
)
from typing import TYPE_CHECKING, Any, Literal

from openbb_core.provider.utils.helpers import amake_request, to_snake_case

if TYPE_CHECKING:
    from pandas import DataFrame

_logger = logging.getLogger(__name__)

TICKER_EXCEPTIONS = ["NDX", "RUT"]

CACHE_NAME = "cboe_directories"
CACHE_MAX_BYTES = 32 * 1024 * 1024
CACHE_SWEEP_PASSES = 3

CACHE_TTL = {
    "*/book/*": 60,
    "*/symbol_lookup_data/*": 3600 * 24,
    "*/trade-optimizer-data/*": 600,
    "*/symbol-info/*": 600,
    "*/GlobalIndices.csv": 900,
    "*/daily_prices/*": 3600 * 6,
    "*/symboldir/*": 3600 * 24,
    "*/definitions/*": 3600 * 24,
    "*/symbol_book/*": 3600 * 24,
    "*": 3600 * 24,
}

AU_INDEX_FILES = "https://cdn.cboe.com/data/au/equities/sgx_index_200"

INDEX_HISTORY_FILES = "https://cdn.cboe.com/api/global/us_indices/daily_prices"

INDEX_FACTSHEETS = "https://cdn.cboe.com/resources/indices/factsheet"

DOCUMENT_HOSTS = {"cdn.cboe.com"}

GLOBAL_INDICES_FEED = (
    "https://cdn.cboe.com/api/global/us_indices/definitions/GlobalIndices.csv"
)

CONSTITUENTS_AU = Literal["X2C", "X2CF", "X2CG", "X2CN"]

CONSTITUENTS_EU = Literal[
    "BAT20P",
    "BBE20P",
    "BCH20P",
    "BCHM30P",
    "BDE40P",
    "BDEM50P",
    "BDES50P",
    "BDK25P",
    "BEP50P",
    "BEPACP",
    "BEPBUS",
    "BEPCNC",
    "BEPCONC",
    "BEPCONS",
    "BEPENGY",
    "BEPFIN",
    "BEPHLTH",
    "BEPIND",
    "BEPNEM",
    "BEPTEC",
    "BEPTEL",
    "BEPUTL",
    "BEPXUKP",
    "BES35P",
    "BEZ50P",
    "BEZACP",
    "BFI25P",
    "BFR40P",
    "BFRM20P",
    "BIE20P",
    "BIT40P",
    "BNL25P",
    "BNLM25P",
    "BNO25G",
    "BNORD40P",
    "BPT20P",
    "BSE30P",
    "BUK100P",
    "BUK250P",
    "BUK350P",
    "BUKAC",
    "BUKBISP",
    "BUKBUS",
    "BUKCNC",
    "BUKCONC",
    "BUKCONS",
    "BUKENGY",
    "BUKFIN",
    "BUKHI50P",
    "BUKHLTH",
    "BUKIND",
    "BUKLO50P",
    "BUKMINP",
    "BUKNEM",
    "BUKSC",
    "BUKTEC",
    "BUKTEL",
    "BUKUTL",
]


def ny_now() -> datetime:
    """Return the current time in the America/New_York timezone."""
    from pytz import timezone

    return datetime.now(tz=timezone("America/New_York"))


def ny_today() -> dateType:
    """Return the current date of the America/New_York trading session."""
    return ny_now().date()


async def response_callback(response, _) -> Any:
    """Deserialize an HTTP client response according to its content type.

    Parameters
    ----------
    response
        The aiohttp client response.
    _
        Unused positional slot required by the callback signature.

    Returns
    -------
    Any
        Parsed JSON, decoded text, or raw bytes.
    """
    content_type = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
        return await response.json()

    if "text" in content_type:
        return await response.text()

    return await response.read()


_cache: Any = None
_swept = False


def cache_path() -> str:
    """Return the file the cached responses are kept in."""
    from openbb_core.app.utils import get_user_cache_directory

    return f"{get_user_cache_directory()}/http/{CACHE_NAME}"


async def _oldest(backend: Any, count: int) -> set:
    """Return the keys of the entries written longest ago."""
    keys: set = set()

    async for key in backend.responses.keys():
        keys.add(key)

        if len(keys) >= count:
            break

    return keys


async def _sweep(backend: Any) -> None:
    """Drop what has expired, then the oldest of what is left if still too big.

    An expiry marks a response stale rather than deleting it, so the file grows
    by every URL ever asked for until something clears it out. It is swept once
    per process. What the sweep leaves over the limit is trimmed by the share
    of the file that overshoots it, which is one rewrite of the file rather than
    one per entry.
    """
    from pathlib import Path

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


async def _vacuum(backend: Any) -> None:
    """Give back the pages the deleted responses were held in."""
    async with backend.responses.get_connection(commit=True) as connection:
        await connection.execute("VACUUM")


async def cache_backend() -> Any:
    """Return the process-wide cache, swept clean on first use.

    Returns
    -------
    Any
        The ``SQLiteBackend`` every cached request shares.
    """
    global _cache, _swept  # noqa: PLW0603

    from aiohttp_client_cache import SQLiteBackend

    if _cache is None:
        _cache = SQLiteBackend(
            cache_path(),
            expire_after=CACHE_TTL["*"],
            urls_expire_after=CACHE_TTL,
        )

    if not _swept:
        _swept = True

        try:
            await _sweep(_cache)
        except Exception:  # noqa: BLE001
            _logger.exception("Sweeping the Cboe response cache failed")

    return _cache


async def get_cboe_data(url: str, use_cache: bool = True, **kwargs) -> Any:
    """Make a request to a Cboe endpoint, optionally through the on-disk cache.

    Parameters
    ----------
    url : str
        The fully-qualified Cboe URL to request.
    use_cache : bool
        When True, the response is cached on disk for as long as the endpoint
        it came from stays good for.

    Returns
    -------
    Any
        The deserialized response.
    """
    from aiohttp_client_cache.session import CachedSession

    if use_cache is not True:
        return await amake_request(url, response_callback=response_callback, **kwargs)

    async with CachedSession(cache=await cache_backend()) as session:
        response = await session.get(url, timeout=10, **kwargs)

        return await response_callback(response, None)


async def get_company_directory(use_cache: bool = True, **kwargs) -> DataFrame:
    """Get the US company directory for Cboe options.

    Parameters
    ----------
    use_cache : bool
        When True, the directory is cached on disk for 24 hours.

    Returns
    -------
    DataFrame
        The Cboe listings directory, indexed by symbol.
    """
    from io import BytesIO

    from pandas import read_csv

    url = "https://www.cboe.com/us/options/symboldir/equity_index_options/?download=csv"
    results = await get_cboe_data(url, use_cache)
    response = BytesIO(results)
    directory = read_csv(response)
    directory = directory.rename(
        columns={
            " Stock Symbol": "symbol",
            " DPM Name": "dpm_name",
            " Post/Station": "post_station",
            "Company Name": "name",
        }
    ).set_index("symbol")

    return directory.astype(str)


async def get_au_index_directory(use_cache: bool = True, **kwargs) -> DataFrame:
    """Get the Cboe Australia (CXA) index directory.

    Parameters
    ----------
    use_cache : bool
        When True, the directory is cached on disk for 24 hours.

    Returns
    -------
    DataFrame
        The CXA index definitions, mapped onto the global directory schema.
    """
    from pandas import DataFrame

    url = "https://cdn.cboe.com/api/global/au_indices/definitions/all-definitions.json"
    response = await get_cboe_data(url, use_cache=use_cache)

    return DataFrame(
        [
            {
                "index_symbol": item["symbol"],
                "name": item.get("short_name"),
                "description": item.get("long_name"),
                "currency": "AUD",
                "source": "au_proprietary_index",
                "time_zone": "Australia/Sydney",
                "index_launch_date": item.get("launch_date"),
                "index_family": item.get("series"),
            }
            for item in response.get("data", [])
        ]
    )


async def get_index_directory(use_cache: bool = True, **kwargs) -> DataFrame:
    """Get the Cboe index directory across every jurisdiction.

    Parameters
    ----------
    use_cache : bool
        When True, the directory is cached on disk for 24 hours.

    Returns
    -------
    DataFrame
        US, European, and Australian Cboe indices, excluding Morningstar-sourced
        rows, annotated with the Global Indices feed channel.
    """
    from pandas import DataFrame, concat

    url = "https://cdn.cboe.com/api/global/us_indices/definitions/all_indices.json"
    results = await get_cboe_data(url, use_cache=use_cache)

    for result in results:
        result.pop("featured", None)
        result.pop("featured_order", None)
        result.pop("display", None)

    directory = DataFrame(results)
    directory = directory[directory["source"] != "morningstar"]
    au_directory = await get_au_index_directory(use_cache=use_cache)
    combined = concat([directory, au_directory], ignore_index=True)

    catalog = await get_global_indices_feed(use_cache=use_cache)
    combined = combined.merge(catalog, on="index_symbol", how="left")

    return combined.astype(object).where(combined.notna(), None)


async def list_futures(**kwargs) -> list[dict]:
    """List the Cboe futures roots and their underlying symbols.

    Returns
    -------
    list[dict]
        One record per futures root.
    """
    response = await get_cboe_data(
        "https://cdn.cboe.com/api/global/delayed_quotes/symbol_book/futures-roots.json"
    )
    data = response.get("data")

    for item in data:
        item.pop("sort_order", None)

    return data


SETTLEMENT_URL = "https://www.cboe.com/us/futures/market_statistics/settlement/csv"
SETTLEMENT_LOOKBACK = 10


async def _get_settlement_csv(url: str, **kwargs) -> DataFrame:
    """Fetch and normalize one settlement price CSV.

    Parameters
    ----------
    url : str
        The settlement CSV to read.

    Returns
    -------
    DataFrame
        The settlement prices, empty when the session published none.
    """
    from io import StringIO

    from pandas import DataFrame, read_csv

    response = await get_cboe_data(url, use_cache=False, **kwargs)
    data = read_csv(StringIO(response), index_col=None, parse_dates=True)

    if data.empty:
        return DataFrame()

    data.columns = [to_snake_case(c) for c in data.columns]

    return data.rename(columns={"expiration_date": "expiration"})


async def get_settlement_prices(
    settlement_date: dateType | None = None,
    options: bool = False,
    archives: bool = False,
    final_settlement: bool = False,
    **kwargs,
) -> DataFrame:
    """Get the settlement prices of Cboe futures.

    Parameters
    ----------
    settlement_date : date | None
        The settlement date. Only valid for active contracts. [YYYY-MM-DD]
    options : bool
        When True, returns options on futures.
    archives : bool
        Settlement price archives for select years and products. Overridden by other parameters.
    final_settlement : bool
        Final settlement prices for expired contracts. Overrides archives.

    Returns
    -------
    DataFrame
        The settlement prices, carrying the session they were published for.
        Weekends and holidays settle nothing, so a date that published no
        prices falls back to the most recent session that did.
    """
    from datetime import timedelta

    from pandas import DataFrame

    if final_settlement is True:
        return await _get_settlement_csv(
            "https://www.cboe.com/us/futures/market_statistics"
            + "/final_settlement_prices/csv/",
            **kwargs,
        )

    if archives is True:
        return await _get_settlement_csv(
            "https://cdn.cboe.com/resources/futures/archive"
            + "/volume-and-price/CFE_FinalSettlement_Archive.csv",
            **kwargs,
        )

    query = "?options=t" if options is True else ""

    if settlement_date is None:
        data = await _get_settlement_csv(SETTLEMENT_URL + query, **kwargs)

        if not data.empty:
            data["settlement_date"] = ny_today().isoformat()

            return data

    session = settlement_date or ny_today()
    separator = "&" if query else "?"

    for offset in range(SETTLEMENT_LOOKBACK):
        day = session - timedelta(days=offset)
        data = await _get_settlement_csv(
            f"{SETTLEMENT_URL}{query}{separator}dt={day}", **kwargs
        )

        if not data.empty:
            data["settlement_date"] = day.isoformat()

            return data

    return DataFrame()


async def get_au_index_constituents(
    symbol: str, session: Literal["eod", "sod"] = "eod"
) -> list[dict]:
    """Get the Cboe Australia (CXA) index constituents and their weights.

    Parameters
    ----------
    symbol : str
        The CXA index symbol - i.e., X2C, X2CF, X2CG, X2CN.
    session : Literal["eod", "sod"]
        'eod' is the last close, 'sod' is the projected next-session open.

    Returns
    -------
    list[dict]
        One record per constituent, carrying the index weight.

    Raises
    ------
    EmptyDataError
        If the file carries no constituent block.
    """
    from csv import DictReader
    from io import StringIO

    from openbb_core.provider.utils.errors import EmptyDataError

    prefix = "AT" if session == "eod" else "PREDICT"
    response = await get_cboe_data(
        f"{AU_INDEX_FILES}/{prefix}_{symbol}.csv", use_cache=False
    )

    if isinstance(response, bytes):
        response = response.decode("utf-8", "ignore")

    lines = response.splitlines()
    header = next(
        (i for i, line in enumerate(lines) if line.startswith("Constituent Name")), None
    )

    if header is None:
        raise EmptyDataError(f"No constituent data was returned for {symbol}.")

    rows = list(DictReader(StringIO("\n".join(lines[header:]))))

    # The block is followed by dividend annotation rows that carry only a name.
    return [row for row in rows if row.get("Weight")]


async def get_index_history(symbol: str, use_cache: bool = True) -> list[dict]:
    """Get the complete published daily history for a Cboe index.

    Parameters
    ----------
    symbol : str
        The Cboe index symbol.
    use_cache : bool
        When True, the file is cached on disk for 24 hours.

    Returns
    -------
    list[dict]
        One record per session, keyed by ``date`` plus the published price columns.

    Raises
    ------
    EmptyDataError
        If Cboe publishes no history for the symbol.
    """
    from csv import DictReader
    from io import StringIO

    from openbb_core.provider.utils.errors import EmptyDataError

    symbol = symbol.replace("^", "").upper()
    response = await get_cboe_data(
        f"{INDEX_HISTORY_FILES}/{symbol}_History.csv", use_cache=use_cache
    )

    if isinstance(response, bytes):
        response = response.decode("utf-8", "ignore")

    if not response or not response.lstrip().upper().startswith("DATE"):
        raise EmptyDataError(f"No published history was found for {symbol}.")

    reader = DictReader(StringIO(response))
    columns = {c: c.lower() for c in (reader.fieldnames or [])}
    columns[symbol] = "close"
    results: list[dict] = []

    for row in reader:
        record = {columns.get(k, k.lower()): v for k, v in row.items() if k}

        if not record.get("date"):
            continue

        results.append(record)

    if not results:
        raise EmptyDataError(f"No published history was found for {symbol}.")

    return results


async def get_global_indices_feed(use_cache: bool = True) -> DataFrame:
    """Get the Cboe Global Indices definition feed catalog.

    Parameters
    ----------
    use_cache : bool
        When True, the catalog is cached on disk for 24 hours.

    Returns
    -------
    DataFrame
        Symbol, description, agent classification, and feed channel for every
        index carried on the Cboe Global Indices feed.
    """
    from io import StringIO

    from pandas import read_csv

    response = await get_cboe_data(GLOBAL_INDICES_FEED, use_cache=use_cache)

    if isinstance(response, bytes):
        response = response.decode("utf-8", "ignore")

    catalog = read_csv(StringIO(response))

    return catalog.rename(
        columns={
            "Symbol": "index_symbol",
            "Agent Classification": "agent_classification",
            "Channel": "channel",
        }
    )[["index_symbol", "agent_classification", "channel"]]


async def get_index_documents(symbol: str | None = None) -> list[dict]:
    """Get the Cboe index documents catalog, optionally scoped to one symbol.

    Parameters
    ----------
    symbol : str | None
        Restrict the result to documents that apply to this index symbol.

    Returns
    -------
    list[dict]
        Records of ``category``, ``title``, and ``url``.
    """
    import json
    from pathlib import Path

    catalog = json.loads(
        (Path(__file__).parents[1] / "assets" / "index_documents.json").read_text(
            encoding="utf-8"
        )
    )

    if not symbol:
        return catalog

    symbol = symbol.replace("^", "").upper()
    factsheet = f"{INDEX_FACTSHEETS}/CboeGlobalIndices_{symbol}-Index.pdf"
    documents = [
        {"category": doc["category"], "title": doc["title"], "url": doc["url"]}
        for doc in catalog
        if symbol in doc.get("symbols", []) or not doc.get("symbols")
    ]

    try:
        await amake_request(factsheet, response_callback=_status_callback)
        documents.insert(
            0,
            {
                "category": "Factsheet",
                "title": f"{symbol} Index Factsheet",
                "url": factsheet,
            },
        )
    except OSError:
        pass

    return documents


async def _status_callback(response, _) -> Any:
    """Raise unless the response is a published document.

    Raises
    ------
    OSError
        If Cboe does not publish the requested document.
    """
    if response.status != 200:
        raise OSError(f"{response.status} for {response.url}")

    return response.status


async def get_index_choices(use_cache: bool = True) -> list[dict[str, str]]:
    """Get ``[{label, value}]`` choices for every index in the Cboe index directory.

    Parameters
    ----------
    use_cache : bool
        When True, the directory is cached on disk for 24 hours.

    Returns
    -------
    list[dict[str, str]]
        Label/value pairs suitable for an OpenBB Workspace dropdown.
    """
    directory = await get_index_directory(use_cache=use_cache)

    return [
        {
            "label": f"{row['index_symbol']} - {row['name']}",
            "value": row["index_symbol"],
        }
        for row in directory.to_dict("records")
    ]


async def get_eu_index_choices(use_cache: bool = True) -> list[dict[str, str]]:
    """Get ``[{label, value}]`` choices for the Cboe indices that publish constituents.

    Parameters
    ----------
    use_cache : bool
        When True, the directory is cached on disk for 24 hours.

    Returns
    -------
    list[dict[str, str]]
        Label/value pairs suitable for an OpenBB Workspace dropdown.
    """
    from typing import get_args

    directory = await get_index_directory(use_cache=use_cache)
    supported = set(get_args(CONSTITUENTS_EU)) | set(get_args(CONSTITUENTS_AU))
    eu_indices = directory[directory["index_symbol"].isin(supported)]

    return [
        {
            "label": f"{row['index_symbol']} - {row['name']}",
            "value": row["index_symbol"],
        }
        for row in eu_indices.to_dict("records")
    ]


async def get_equity_choices(use_cache: bool = True) -> list[dict[str, str]]:
    """Get ``[{label, value}]`` choices for every symbol in the Cboe company directory.

    Parameters
    ----------
    use_cache : bool
        When True, the directory is cached on disk for 24 hours.

    Returns
    -------
    list[dict[str, str]]
        Label/value pairs suitable for an OpenBB Workspace dropdown.
    """
    directory = await get_company_directory(use_cache=use_cache)

    return [
        {"label": f"{symbol} - {name}", "value": symbol}
        for symbol, name in zip(directory.index.tolist(), directory["name"].tolist())
        if isinstance(symbol, str)
    ]


async def get_document_choices(symbol: str | None = None) -> list[dict]:
    """Get ``[{label, value}]`` choices of index documents, as PDF URLs.

    Parameters
    ----------
    symbol : str | None
        Restrict the choices to documents that apply to this index symbol.

    Returns
    -------
    list[dict]
        Label/value pairs where the value is the document URL.
    """
    documents = await get_index_documents(symbol)

    return [
        {
            "label": f"{doc['category']} - {doc['title']}",
            "value": doc["url"],
            "extraInfo": {"description": doc["title"]},
        }
        for doc in documents
        if doc.get("url")
    ]


def is_cboe_document_url(url: Any) -> bool:
    """Return True only for an https URL on a Cboe document host.

    Parameters
    ----------
    url : Any
        The value to check.

    Returns
    -------
    bool
        Whether the value is a fully-qualified Cboe document URL.
    """
    from urllib.parse import urlparse

    if not isinstance(url, str):
        return False

    parsed = urlparse(url)

    return parsed.scheme == "https" and parsed.hostname in DOCUMENT_HOSTS


async def download_index_document(document_url: str) -> str:
    """Download an index document and return it base64-encoded.

    Parameters
    ----------
    document_url : str
        The fully-qualified PDF URL, on a Cboe document host.

    Returns
    -------
    str
        The base64-encoded document.

    Raises
    ------
    OSError
        If the URL is not on a Cboe document host.
    """
    import base64

    from openbb_core.provider.utils.helpers import amake_request

    if not is_cboe_document_url(document_url):
        raise OSError(f"Refusing to download a non-Cboe document: {document_url}")

    async def read(response, _):
        """Return the raw response body."""
        return await response.read()

    content = await amake_request(document_url, response_callback=read)

    return base64.b64encode(content).decode("utf-8")  # ty: ignore[invalid-argument-type]


async def open_index_document(document_url: str) -> dict:
    """Open one index document for the Workspace multi-file viewer.

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
        encoded = await download_index_document(document_url)
    except Exception as exc:  # noqa: BLE001
        return {
            "error_type": "download_error",
            "content": f"Error fetching document: {exc}",
        }

    return {
        "content": encoded,
        "data_format": {
            "data_type": "pdf",
            "filename": document_url.rsplit("/", 1)[-1] or "document.pdf",
        },
    }
