"""Cboe Europe equities transport - symbology and the venue order books."""

from typing import Any, Literal

EU_MARKETS = ("bxe", "cxe", "dxe", "sis")

EuMarket = Literal["bxe", "cxe", "dxe", "sis"]

BOOK_VIEWER = "https://www.cboe.com/europe/equities/market_statistics/book_viewer/"
BOOK_URL = "https://ww2.cboe.com/json/{market}/book/{symbol}"
LOOKUP_URL = (
    "https://ww2.cboe.com/europe/equities/market_statistics/book_viewer_2"
    "/symbol_lookup_data/?mkt={market}"
)


def _headers() -> dict:
    """Build the headers the venue endpoints answer to."""
    return {
        "Accept": "application/json",
        "Referer": BOOK_VIEWER,
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
            " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        ),
    }


async def get_eu_symbol_directory(
    market: EuMarket = "cxe", use_cache: bool = True
) -> list[dict]:
    """Get every symbol one Cboe Europe venue lists.

    Parameters
    ----------
    market : EuMarket
        The venue, one of BXE, CXE, DXE, or SIS.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    list[dict]
        One entry per listing, carrying its symbol, company, and ISIN.

    Raises
    ------
    OpenBBError
        If the venue publishes no symbology.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cboe.utils.helpers import get_cboe_data

    response = await get_cboe_data(
        LOOKUP_URL.format(market=market), use_cache=use_cache, headers=_headers()
    )
    listings = (response or {}).get("symbolsLookupData")

    if not listings:
        raise OpenBBError(f"No symbology was returned for {market.upper()}.")

    return [
        {
            "symbol": listing.get("name"),
            "name": listing.get("company_name"),
            "isin": listing.get("isin"),
            "market": market.upper(),
        }
        for listing in listings
        if listing.get("name")
    ]


async def get_eu_company_names(use_cache: bool = True) -> dict[str, str]:
    """Map every Cboe Europe symbol to its company name, across the venues.

    Parameters
    ----------
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict[str, str]
        The company name published for each symbol.
    """
    import asyncio

    async def one(market: EuMarket) -> list[dict]:
        try:
            return await get_eu_symbol_directory(market, use_cache=use_cache)
        except Exception:  # noqa: BLE001
            return []

    directories = await asyncio.gather(*[one(market) for market in EU_MARKETS])
    names: dict[str, str] = {}

    for listings in directories:
        for listing in listings:
            if listing["symbol"] and listing["name"]:
                names.setdefault(listing["symbol"], listing["name"])

    return names


async def get_eu_book(
    symbol: str, market: EuMarket = "cxe", use_cache: bool = True
) -> dict[str, Any]:
    """Get one venue's book and session statistics for a symbol.

    Parameters
    ----------
    symbol : str
        The Cboe Europe symbol, as the venue lists it.
    market : EuMarket
        The venue, one of BXE, CXE, DXE, or SIS.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    dict[str, Any]
        The session statistics, the resting orders, and the trade tape.

    Raises
    ------
    OpenBBError
        If the venue does not list the symbol.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cboe.utils.helpers import get_cboe_data

    response = await get_cboe_data(
        BOOK_URL.format(market=market, symbol=symbol),
        use_cache=use_cache,
        headers=_headers(),
    )

    if not isinstance(response, dict) or not response.get("success"):
        raise OpenBBError(f"No book was returned for {symbol} on {market.upper()}.")

    data = response.get("data") or {}

    if not data.get("company") and data.get("last") in (None, 0):
        raise OpenBBError(f"{symbol} is not listed on {market.upper()}.")

    return data
