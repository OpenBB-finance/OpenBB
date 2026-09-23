"""Deribit shared response cache."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp_client_cache import SQLiteBackend

MINUTE = 60
HOUR = 60 * 60
DAY = 60 * 60 * 24

CACHE_NAME = "deribit"
CACHE_TTL_DEFAULT = 5 * MINUTE
CACHE_MAX_BYTES = 128 * 1024 * 1024
CACHE_SWEEP_PASSES = 3

URL_CACHE_TTL = {
    "*/public/get_currencies*": DAY,
    "*/public/get_index_price_names*": DAY,
    "*/public/get_supported_index_names*": DAY,
    "*/public/get_instruments*": HOUR,
    "*/public/get_instrument*": HOUR,
    "*/public/get_contract_size*": DAY,
    "*/public/get_expirations*": HOUR,
    "*/public/get_combo_ids*": HOUR,
    "*/public/get_combos*": HOUR,
    "*/public/get_combo_details*": HOUR,
    "*/public/get_delivery_prices*": HOUR,
    "*/public/get_apr_history*": HOUR,
    "*/public/get_announcements*": HOUR,
    "*/public/get_trade_volumes*": 15 * MINUTE,
    "*/public/get_historical_volatility*": 15 * MINUTE,
    "*/public/get_volatility_index_data*": 15 * MINUTE,
    "*/public/get_funding_rate_history*": 15 * MINUTE,
    "*/public/get_funding_chart_data*": 5 * MINUTE,
    "*/public/get_funding_rate_value*": 5 * MINUTE,
    "*/public/get_mark_price_history*": 5 * MINUTE,
    "*/public/get_tradingview_chart_data*": 5 * MINUTE,
    "*/public/get_index_chart_data*": 5 * MINUTE,
    "*/public/get_last_settlements_by_currency*": 5 * MINUTE,
    "*/public/get_last_settlements_by_instrument*": 5 * MINUTE,
    "*/public/get_block_rfq_trades*": MINUTE,
    "*/public/get_last_trades_by_currency*": MINUTE,
    "*/public/get_last_trades_by_instrument*": MINUTE,
    "*/public/get_book_summary_by_currency*": MINUTE,
    "*/public/get_book_summary_by_instrument*": MINUTE,
    "*/public/get_index_price*": MINUTE,
    "*/public/get_order_book*": 0,
    "*/public/ticker*": 0,
    "*/public/get_time*": 0,
    "*/public/status*": 0,
}

_swept = False


def cache_path() -> str:
    """Return the file the cached responses are kept in."""
    from openbb_core.app.utils import get_user_cache_directory

    return f"{get_user_cache_directory()}/http/{CACHE_NAME}"


def get_cache_backend() -> "SQLiteBackend":
    """Build the on-disk response cache, with a TTL per endpoint.

    Returns
    -------
    SQLiteBackend
        The shared response cache.
    """
    from aiohttp_client_cache import SQLiteBackend

    return SQLiteBackend(
        cache_name=cache_path(),
        expire_after=CACHE_TTL_DEFAULT,
        urls_expire_after=URL_CACHE_TTL,
        allowed_codes=(200,),
        allowed_methods=("GET",),
        include_headers=False,
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
        await connection.execute("VACUUM")


async def sweep_cache(backend: "SQLiteBackend") -> None:
    """Drop what has expired, then the oldest of what is left if still too big.

    An expiry marks a response stale rather than deleting it, so the file grows
    by every request ever made until something clears it out. It is swept once
    per process, and what the sweep leaves over the limit is trimmed by the
    share of the file that overshoots it.

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
