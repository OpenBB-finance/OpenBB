"""The FINRA traded-security list, classified by security type."""

from typing import Any


def read_asset() -> dict:
    """Return the bundled security-type asset.

    Returns
    -------
    dict
        The classification of every symbol known at build time, and the
        symbols that could not be classified.
    """
    import gzip
    import json

    from openbb_finra.utils.generate_securities import ASSET_PATH

    try:
        return json.loads(gzip.decompress(ASSET_PATH.read_bytes()))
    except (OSError, ValueError):
        return {"securities": {}, "unresolved": []}


async def load_universe() -> dict[str, dict]:
    """Return every symbol FINRA published OTC or ATS volume for in its latest weeks.

    Returns
    -------
    dict[str, dict]
        The FINRA issue name, tier, and product type of each symbol.
    """
    import asyncio

    from openbb_finra.utils.client import query_api_session
    from openbb_finra.utils.generate_securities import (
        SUMMARY_TYPES,
        latest_weeks,
        merge_universe,
        universe_payload,
    )

    async with query_api_session() as api:
        weeks = latest_weeks(await api.partitions("otcMarket", "weeklySummary"))
        pages = await asyncio.gather(
            *(
                api.query(
                    "otcMarket",
                    "weeklySummary",
                    universe_payload(week, tier, summary_type),
                )
                for tier, week in sorted(weeks.items())
                for summary_type in SUMMARY_TYPES
            )
        )

    universe: dict[str, dict] = {}

    for rows in pages:
        merge_universe(universe, rows)

    return universe


async def _lookup(
    market_data: Any, symbols: list[str], prefix: str | None = None
) -> dict[str, list]:
    """Classify one batch, isolating symbols the service rejects.

    Raises
    ------
    OpenBBError
        If the service keeps throttling the lookups.
    """
    import asyncio

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_finra.utils import constants
    from openbb_finra.utils.client import (
        MarketDataRejectedError,
        MarketDataThrottledError,
    )
    from openbb_finra.utils.generate_securities import lookup_form, read_lookup

    for attempt in range(1, constants.LOOKUP_ATTEMPTS + 1):
        try:
            records = await market_data.lookup(
                [lookup_form(symbol, prefix) for symbol in symbols]
            )
        except MarketDataThrottledError:
            await asyncio.sleep(constants.LOOKUP_THROTTLE_WAIT * attempt)
            await market_data.seed()
            continue
        except MarketDataRejectedError:
            if len(symbols) == 1:
                return {}

            middle = len(symbols) // 2

            return {
                **await _lookup(market_data, symbols[:middle], prefix),
                **await _lookup(market_data, symbols[middle:], prefix),
            }

        return read_lookup(records, symbols, prefix)

    raise OpenBBError("The FINRA Market Data Center kept throttling the lookups.")


async def classify_symbols(universe: dict[str, dict]) -> dict[str, list]:
    """Return the Market Data Center classification of symbols on US markets.

    Parameters
    ----------
    universe : dict[str, dict]
        The FINRA symbols to classify, with their tiers.

    Returns
    -------
    dict[str, list]
        The compact classification of each symbol that resolved.
    """
    from openbb_finra.utils.client import market_data_session
    from openbb_finra.utils.generate_securities import batches, lookup_plan

    if not universe:
        return {}

    symbols = sorted(universe)
    classes: dict[str, list] = {}

    async with market_data_session() as market_data:
        for prefix, group in lookup_plan(universe, symbols).items():
            for batch in batches(group):
                classes.update(await _lookup(market_data, batch, prefix))

        for batch in batches([symbol for symbol in symbols if symbol not in classes]):
            classes.update(await _lookup(market_data, batch))

    return classes


async def list_securities() -> list[dict]:
    """Return every traded symbol with its FINRA and Market Data Center details.

    Returns
    -------
    list[dict]
        One row per symbol, sorted by symbol.
    """
    from openbb_finra.utils.constants import MARKET_DATA_DETAIL_URL
    from openbb_finra.utils.generate_securities import CLASS_FIELDS

    universe = await load_universe()
    asset = read_asset()
    known = asset.get("securities") or {}
    unresolved = set(asset.get("unresolved") or [])
    classes = {
        **known,
        **await classify_symbols(
            {
                symbol: details
                for symbol, details in universe.items()
                if symbol not in known and symbol not in unresolved
            }
        ),
    }
    rows = []

    for symbol, finra in sorted(universe.items()):
        row = {
            "symbol": symbol,
            **finra,
            **dict(zip(CLASS_FIELDS, classes.get(symbol) or [])),
        }
        listing, performance = row.get("listing_market_id"), row.get("performance_id")
        row["url"] = (
            f"{MARKET_DATA_DETAIL_URL}?query={listing}:{performance}"
            if listing and performance
            else None
        )
        rows.append(row)

    return rows
