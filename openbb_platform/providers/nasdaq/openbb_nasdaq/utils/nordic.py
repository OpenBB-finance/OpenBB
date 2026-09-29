"""Nasdaq Nordic Constants and Instrument Resolution."""

from typing import Literal

from async_lru import alru_cache

NORDIC_BASE_URL = "https://api.nasdaq.com/api/nordic/screener"

NORDIC_NEWS_URL = "https://api.news.eu.nasdaq.com/news/query.action"

NORDIC_ASSET_CLASSES = Literal[
    "shares",
    "indexes",
    "funds",
    "etf",
    "etn_etc",
    "aif",
    "amf",
    "options",
    "custom_basket_forwards",
    "corporate_bonds",
    "government_bonds",
    "mortgage_bonds",
    "sustainable_debt",
    "fi_derivatives",
    "structured_products",
    "warrants",
    "certificates",
    "leverage_certificates",
    "tracker_certificates",
]

NORDIC_PATHS = {
    "shares": "shares",
    "indexes": "indexes",
    "funds": "funds",
    "etf": "etp",
    "etn_etc": "etp",
    "aif": "etp",
    "amf": "etp",
    "options": "options",
    "custom_basket_forwards": "custom-basket-forwards",
    "corporate_bonds": "corporate-bonds",
    "government_bonds": "government-bonds",
    "mortgage_bonds": "mortgage-bonds",
    "sustainable_debt": "sustainable-debt",
    "fi_derivatives": "fi-derivatives",
    "structured_products": "structured-products",
    "warrants": "warrants-certificates",
    "certificates": "warrants-certificates",
    "leverage_certificates": "warrants-certificates",
    "tracker_certificates": "warrants-certificates",
}

NORDIC_MARKETS = Literal[
    "main_market",
    "first_north",
    "other_instruments",
    "sweden",
    "denmark",
    "finland",
    "iceland",
]

NORDIC_MARKET_KEYS = {
    "main_market": "MAIN_MARKET",
    "first_north": "FIRST_NORTH",
    "other_instruments": "OTHERS",
    "sweden": "STO_MM",
    "denmark": "CPH_MM",
    "finland": "HEL_MM",
    "iceland": "ICE_MM",
}

NORDIC_SHARE_MARKETS = ("main_market", "first_north", "other_instruments")

NORDIC_COUNTRY_MARKETS = ("sweden", "denmark", "finland", "iceland")

# Nasdaq rejects the markets a listing does not serve, so the segmented
# listings carry only the countries that actually answer.
NORDIC_MORTGAGE_MARKETS = ("denmark", "sweden", "iceland")

NORDIC_FI_DERIVATIVE_MARKETS = ("denmark", "sweden")

NORDIC_CATEGORIES = {
    "shares": NORDIC_SHARE_MARKETS,
    "corporate_bonds": NORDIC_COUNTRY_MARKETS,
    "government_bonds": NORDIC_COUNTRY_MARKETS,
    "mortgage_bonds": NORDIC_MORTGAGE_MARKETS,
    "sustainable_debt": NORDIC_COUNTRY_MARKETS,
    "fi_derivatives": NORDIC_FI_DERIVATIVE_MARKETS,
    "structured_products": NORDIC_COUNTRY_MARKETS,
}

NORDIC_FIXED_CATEGORIES = {
    "warrants": "WARRANTS",
    "certificates": "CERTIFICATES",
    "leverage_certificates": "LEVERAGE_CERTIFICATES",
    "tracker_certificates": "TRACKER_CERTIFICATES",
    "etf": "ETF",
    "etn_etc": "ETN/ETC",
    "aif": "AIF",
    "amf": "AMF",
}

# The index listing is segmented by ``market`` rather than ``category``, and it
# serves one group at a time, so a complete directory has to walk every group.
NORDIC_INDEX_MARKETS = (
    "NOK_ALL",
    "NOK_SH_IN",
    "NOK_SC_IN",
    "CPH_SH_IN",
    "CPH_SC_IN",
    "STO_SH_IN",
    "STO_SC_IN",
    "STO_FI_IN",
    "HEL_SH_IN",
    "HEL_SC_IN",
    "ICE_SH_IN",
    "ICE_SC_IN",
    "ICE_FI_IN",
    "FS_NT_IDXS",
    "OSL",
    "VINX_SH_IN",
    "VINX_SC_IN_IND",
    "VINX_SC_IN_SUS",
    "CSTM_IDXS",
)

NORDIC_NEWS_MARKETS = Literal[
    "all",
    "stockholm",
    "copenhagen",
    "helsinki",
    "iceland",
    "baltic",
    "first_north",
]

NORDIC_NEWS_MARKET_KEYS = {
    "all": "NordicAllMarkets",
    "stockholm": "Stockholm",
    "copenhagen": "Copenhagen",
    "helsinki": "Helsinki",
    "iceland": "Iceland",
    "baltic": "Baltic",
    "first_north": "FirstNorth",
}

NORDIC_NUMBER_FIELDS = {
    "last_price": "lastSalePrice",
    "change": "netChange",
    "bid": "bidPrice",
    "ask": "askPrice",
    "high": "high",
    "low": "low",
    "volume": "volume",
    "reported_volume": "reportedVolume",
    "total_volume": "totalVolume",
    "turnover": "turnover",
    "trades_count": "tradesCount",
    "net_asset_value": "netAssetValue",
    "average_price": "allTradesAvgPrice",
    "settlement_price": "settlementPrice",
    "coupon_rate": "couponRate",
    "strike": "strikePrice",
    "contract_size": "contractSize",
    "open_interest": "openInterest",
    "basket_value": "basketValue",
    "theoretical_price": "theoreticalPrice",
    "deferral_threshold": "deferralThreshold",
}

NORDIC_TEXT_FIELDS = {
    "name": "fullName",
    "isin": "isin",
    "currency": "currency",
    "sector": "sector",
    "issuer": "issuerFullName",
    "orderbook_id": "orderbookId",
    "mic_code": "micCode",
    "price_notation": "priceNotation",
    "note_code": "noteCode",
    "note_description": "noteDescription",
    "instrument_type": "type",
    "exchange_symbol": "exchangeSymbol",
    "green_equity_designation": "greenEquityDesignation",
}

NORDIC_PROBE_ORDER = (
    "shares",
    "indexes",
    "funds",
    "etf",
    "etn_etc",
    "aif",
    "amf",
    "options",
    "custom_basket_forwards",
    "corporate_bonds",
    "government_bonds",
    "mortgage_bonds",
    "sustainable_debt",
    "fi_derivatives",
    "structured_products",
    "warrants",
    "certificates",
    "leverage_certificates",
    "tracker_certificates",
)

NORDIC_TRADE_FIELDS = {
    "price": "price",
    "volume": "volume",
    "buyer": "buyer",
    "seller": "seller",
    "trade_type": "tradeType",
    "market": "market",
    "mmt_flag": "mmtFlag",
    "orderbook": "orderbook",
    "cancelled": "cancelled",
    "agreement_time": "agreementTime",
}

NORDIC_PRICE_FIELDS = {
    "high": "high",
    "low": "low",
    "close": "close",
    "average_price": "atap",
    "volume": "totalVolume",
    "turnover": "turnover",
    "duration": "duration",
    "yield_to_maturity": "yield",
    "yield_calculation_price": "ycp",
    "reference_price": "priceAPA",
    "consolidated_volume": "volumeAPA",
    "consolidated_turnover": "turnoverAPA",
}


DIRECTORY_PAGE_SIZE = 1000

# The directory fans out across every listing at once. Under load Nasdaq
# refuses a page by returning it empty rather than by erroring, which would
# silently shrink the directory, so the fan-out is bounded and a page that
# comes back empty when the listing claims more is retried.
DIRECTORY_CONCURRENCY = 16

DIRECTORY_ATTEMPTS = 3

DIRECTORY_BACKOFF = 0.5


def _directory_requests() -> list[tuple[str, str, str]]:
    """List every ``(listing, path, filter)`` the directory has to fetch.

    Returns
    -------
    list[tuple]
        One entry per listing, expanded across the markets or index groups a
        listing is segmented by. The filter is the ready-made query fragment,
        because indexes are keyed by ``market`` and everything else by
        ``category``.
    """
    combinations: list[tuple[str, str, str]] = []

    for listing in NORDIC_PROBE_ORDER:
        path = NORDIC_PATHS[listing]
        fixed = NORDIC_FIXED_CATEGORIES.get(listing)
        markets = NORDIC_CATEGORIES.get(listing)

        if listing == "indexes":
            combinations.extend(
                (listing, path, f"&market={group}") for group in NORDIC_INDEX_MARKETS
            )
        elif markets:
            combinations.extend(
                (listing, path, f"&category={NORDIC_MARKET_KEYS[market]}")
                for market in markets
            )
        else:
            combinations.append((listing, path, f"&category={fixed}" if fixed else ""))

    return combinations


async def _directory_page(path: str, query: str, page: int) -> tuple:
    """Fetch one page of a listing and report how many pages it has.

    Raises
    ------
    OpenBBError
        If the page is still refused after every attempt.
    """
    import asyncio

    from openbb_nasdaq.utils.helpers import get_nasdaq_data

    url = (
        f"nordic/screener/{path}?tableonly=true&lang=en"
        f"&size={DIRECTORY_PAGE_SIZE}&page={page}{query}"
    )

    for attempt in range(DIRECTORY_ATTEMPTS):
        try:
            data = await get_nasdaq_data(url, use_cache=False) or {}
        except Exception:  # noqa: BLE001
            if attempt == DIRECTORY_ATTEMPTS - 1:
                raise

            await asyncio.sleep(DIRECTORY_BACKOFF * (attempt + 1))

            continue

        listing = data.get("instrumentListing") or {}
        rows = listing.get("rows") or data.get("rows") or []
        pages = int((data.get("pagination") or {}).get("totalPages") or 1)

        if rows or page == 1 or attempt == DIRECTORY_ATTEMPTS - 1:
            return rows, pages

        await asyncio.sleep(DIRECTORY_BACKOFF * (attempt + 1))

    return [], 1  # pragma: no cover


@alru_cache(maxsize=1)
async def get_nordic_directory() -> dict:
    """Index every Nasdaq Nordic listing into one symbol directory.

    Nasdaq keys its instrument endpoints by an opaque orderbook ID and an asset
    class. Neither is something a caller should have to supply, so every
    listing is indexed once per process and the symbol alone resolves both.
    Each listing's first page reports its page count, so the remainder are
    fetched in a single parallel pass rather than walked in sequence.

    Returns
    -------
    dict
        Symbol mapped to ``{'orderbook_id', 'asset_class', 'listing', 'name',
        'isin'}``, across every asset class Nasdaq Nordic publishes.
    """
    import asyncio

    combinations = _directory_requests()
    directory: dict[str, dict] = {}
    semaphore = asyncio.Semaphore(DIRECTORY_CONCURRENCY)

    async def page(path: str, query: str, number: int) -> tuple:
        """Fetch one page while holding a concurrency slot."""
        async with semaphore:
            return await _directory_page(path, query, number)

    def absorb(listing: str, rows: list) -> None:
        """Index the rows of one page, keeping the first listing to claim a symbol."""
        for row in rows:
            symbol = row.get("symbol")

            if not symbol or symbol in directory:
                continue

            directory[symbol] = {
                "orderbook_id": row.get("orderbookId"),
                "asset_class": row.get("assetClass"),
                "listing": listing,
                "name": row.get("fullName"),
                "isin": row.get("isin"),
            }

    firsts = await asyncio.gather(
        *[page(path, query, 1) for _, path, query in combinations],
        return_exceptions=True,
    )
    remaining: list = []

    for (listing, path, query), result in zip(combinations, firsts):
        if isinstance(result, BaseException):
            continue

        rows, pages = result
        absorb(listing, rows)
        remaining.extend(
            (listing, page(path, query, number)) for number in range(2, pages + 1)
        )

    if remaining:
        pages = await asyncio.gather(
            *[coroutine for _, coroutine in remaining], return_exceptions=True
        )

        for (listing, _), result in zip(remaining, pages):
            if not isinstance(result, BaseException):
                absorb(listing, result[0])

    return directory


async def resolve_nordic_instrument(symbol: str) -> dict:
    """Resolve a Nasdaq Nordic symbol to its orderbook identifier.

    Parameters
    ----------
    symbol : str
        The instrument symbol as listed by Nasdaq Nordic.

    Returns
    -------
    dict
        The record with 'orderbook_id', 'asset_class', 'listing', 'name', and
        'isin'.

    Raises
    ------
    OpenBBError
        If no listing carries the symbol.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    directory = await get_nordic_directory()
    found = directory.get(symbol.strip().upper())

    if found is None:
        raise OpenBBError(
            f"'{symbol}' was not found in the Nasdaq Nordic instrument directory."
        )

    return found


NORDIC_MOVER_TYPES = Literal[
    "shares",
    "options_futures",
    "etp",
    "funds",
    "indexes",
    "warrants_certificates",
]

NORDIC_MOVER_GROUPS = {
    "shares": "SHARES",
    "options_futures": "OPTIONS_FUTURES",
    "etp": "ETP",
    "funds": "FUNDS",
    "indexes": "INDEXES",
    "warrants_certificates": "WARRANTS_CERTIFICATES",
}


@alru_cache(maxsize=1)
async def get_nordic_symbol_choices() -> list[dict]:
    """Get ``[{label, value}]`` choices for every Nasdaq Nordic instrument.

    Returns
    -------
    list[dict]
        Label/value pairs suitable for an OpenBB Workspace dropdown, carrying
        the instrument name, asset class, and ISIN as the description.
    """
    directory = await get_nordic_directory()
    choices: list[dict] = []

    for symbol, record in sorted(directory.items()):
        name = record.get("name") or symbol
        isin = record.get("isin")
        listing = str(record.get("listing") or "").replace("_", " ")
        description = f"{name} - {listing}"
        choices.append(
            {
                "label": symbol,
                "value": symbol,
                "extraInfo": {
                    "description": f"{description} ({isin})" if isin else description,
                },
            }
        )

    return choices
