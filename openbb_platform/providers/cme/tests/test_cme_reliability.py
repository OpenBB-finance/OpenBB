"""Failure-injection tests for CME transport and catalog reliability."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.provider.utils.helpers import run_async

from openbb_cme.models.futures_historical import CMEFuturesHistoricalFetcher
from openbb_cme.models.options_chains import CMEOptionsChainsFetcher
from openbb_cme.utils.catalog import (
    _read_disk_cache,
    clear_catalog_cache,
    fetch_product_catalog,
)
from openbb_cme.utils.client import CMEHttpClient, CMERequestError
from openbb_cme.utils.helpers import fetch_settlements

_URL = "https://www.cmegroup.com/test"
_PRODUCT = {
    "product_id": 133,
    "guid": "ES-GUID",
    "symbol": "ES",
    "name": "E-mini S&P 500 Futures",
    "product_type": "Futures",
    "asset_class": "Equities",
    "subgroup": "S&P",
    "category": None,
    "subcategory": None,
    "exchange": "CME",
    "venues": ["Globex"],
    "globex_traded": True,
    "floor_traded": False,
    "volume": 1,
    "open_interest": 1,
    "codes": {"globex": "ES"},
    "specification_url": "https://www.cmegroup.com/markets/es",
}


class _Response:
    """Minimal curl-cffi response double."""

    def __init__(
        self,
        status_code: int,
        payload=None,
        *,
        headers: dict | None = None,
        json_error: Exception | None = None,
    ):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self._json_error = json_error

    def raise_for_status(self):
        """Raise for HTTP errors."""
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        """Return the configured payload."""
        if self._json_error:
            raise self._json_error
        return self._payload


class _Session:
    """Minimal asynchronous session double."""

    def __init__(self, responses):
        self._responses = iter(responses)
        self.get = AsyncMock(side_effect=self._get)
        self.close = AsyncMock()

    async def _get(self, *_args, **_kwargs):
        result = next(self._responses)
        if isinstance(result, Exception):
            raise result
        return result


def test_http_client_retries_429_and_honors_retry_after():
    """A throttled request waits and succeeds without surfacing partial failure."""
    session = _Session(
        [
            _Response(429, {}, headers={"Retry-After": "1.5"}),
            _Response(200, {"ok": True}),
        ]
    )

    async def run():
        async with CMEHttpClient(
            session=session,
            min_interval=0,
            max_attempts=3,
        ) as client:
            return await client.get_json(_URL)

    with patch("openbb_cme.utils.client.asyncio.sleep", new=AsyncMock()) as mock_sleep:
        result = run_async(run)

    assert result == {"ok": True}
    assert session.get.await_count == 2
    mock_sleep.assert_awaited_once_with(1.5)


def test_http_client_reuses_and_closes_owned_session():
    """Multiple requests share one session, which is closed at operation end."""
    session = _Session(
        [
            _Response(200, {"page": 1}),
            _Response(200, {"page": 2}),
        ]
    )

    async def run():
        async with CMEHttpClient(min_interval=0) as client:
            first = await client.get_json(f"{_URL}/1")
            second = await client.get_json(f"{_URL}/2")
            return first, second

    with patch(
        "curl_cffi.requests.AsyncSession",
        return_value=session,
    ) as session_factory:
        assert run_async(run) == ({"page": 1}, {"page": 2})

    session_factory.assert_called_once_with(impersonate="chrome120")
    assert session.get.await_count == 2
    session.close.assert_awaited_once()


def test_http_client_exhausts_retryable_statuses():
    """Retryable upstream errors become a typed error after a bounded attempt count."""
    session = _Session([_Response(503, {}) for _ in range(3)])

    async def run():
        async with CMEHttpClient(
            session=session,
            min_interval=0,
            backoff=0,
            max_attempts=3,
        ) as client:
            return await client.get_json(_URL)

    with pytest.raises(CMERequestError) as exc_info:
        run_async(run)

    assert exc_info.value.status_code == 503
    assert exc_info.value.attempts == 3
    assert session.get.await_count == 3


def test_http_client_does_not_retry_non_retryable_status():
    """A permanent client error fails immediately."""
    session = _Session([_Response(404, {})])

    async def run():
        async with CMEHttpClient(
            session=session,
            min_interval=0,
            max_attempts=4,
        ) as client:
            return await client.get_json(_URL)

    with pytest.raises(CMERequestError) as exc_info:
        run_async(run)

    assert exc_info.value.status_code == 404
    assert exc_info.value.attempts == 1
    assert session.get.await_count == 1


@pytest.mark.parametrize(
    "response",
    [
        _Response(200, "not-an-object"),
        _Response(200, json_error=ValueError("invalid JSON")),
    ],
)
def test_http_client_rejects_invalid_payloads(response):
    """HTML challenges and schema-incompatible JSON fail explicitly."""
    session = _Session([response])

    async def run():
        async with CMEHttpClient(
            session=session, min_interval=0, max_attempts=1
        ) as client:
            return await client.get_json(_URL)

    with pytest.raises(CMERequestError, match="invalid JSON|unexpected JSON"):
        run_async(run)


def test_http_client_recovers_from_transient_invalid_json():
    """A temporary HTML challenge is retried before returning valid JSON."""
    session = _Session(
        [
            _Response(200, json_error=ValueError("HTML challenge")),
            _Response(200, {"ok": True}),
        ]
    )

    async def run():
        async with CMEHttpClient(
            session=session,
            min_interval=0,
            backoff=0,
        ) as client:
            return await client.get_json(_URL)

    assert run_async(run) == {"ok": True}
    assert session.get.await_count == 2


def test_catalog_refresh_is_single_flight():
    """Concurrent cold-cache readers share one catalog refresh."""
    clear_catalog_cache()

    async def delayed_catalog(*_args, **_kwargs):
        await asyncio.sleep(0)
        return [_PRODUCT]

    async def run():
        return await asyncio.gather(
            fetch_product_catalog("Futures", client=object()),
            fetch_product_catalog("Futures", client=object()),
        )

    with (
        patch("openbb_cme.utils.catalog._read_disk_cache", return_value=None),
        patch("openbb_cme.utils.catalog._write_disk_cache"),
        patch(
            "openbb_cme.utils.catalog._fetch_product_catalog",
            new=AsyncMock(side_effect=delayed_catalog),
        ) as mock_fetch,
    ):
        first, second = run_async(run)

    assert first == second == [_PRODUCT]
    assert first is not second
    mock_fetch.assert_awaited_once()
    clear_catalog_cache()


def test_catalog_uses_bounded_stale_cache_when_refresh_fails():
    """A recent durable cache keeps symbol resolution available during an outage."""
    clear_catalog_cache()
    stale = (900.0, [_PRODUCT])
    error = CMERequestError("offline", url=_URL)

    async def run():
        return await fetch_product_catalog("Futures", client=object())

    with (
        patch("openbb_cme.utils.catalog.time.time", return_value=1000.0),
        patch("openbb_cme.utils.catalog._CACHE_TTL_SECONDS", 10.0),
        patch("openbb_cme.utils.catalog._STALE_CACHE_TTL_SECONDS", 200.0),
        patch("openbb_cme.utils.catalog._read_disk_cache", return_value=stale),
        patch(
            "openbb_cme.utils.catalog._refresh_product_catalog",
            new=AsyncMock(side_effect=error),
        ),
        pytest.warns(RuntimeWarning, match="using the most recent cached catalog"),
    ):
        result = run_async(run)

    assert result == [_PRODUCT]
    clear_catalog_cache()


def test_catalog_rejects_corrupt_persistent_cache(tmp_path):
    """Truncated or malformed disk caches are ignored."""
    cache_file = tmp_path / "product_catalog_futures.json"
    cache_file.write_text("{truncated", encoding="utf-8")
    with patch(
        "openbb_cme.utils.catalog._catalog_cache_path",
        return_value=cache_file,
    ):
        assert _read_disk_cache("Futures") is None


def test_historical_fetch_fails_atomically_on_one_upstream_error():
    """A failed date must not be silently omitted from a historical response."""
    product = {**_PRODUCT, "product_id": 133}
    row = {
        "date": date(2025, 6, 24),
        "symbol": "ES",
        "expiration": "2025-09",
        "close": 6000.0,
        "settlement_price": 6000.0,
    }

    async def settlements(_symbol, trade_date, _product_id, _client):
        if trade_date == date(2025, 6, 25):
            raise CMERequestError("upstream failed", url=_URL)
        return [{**row, "date": trade_date}]

    with (
        patch(
            "openbb_cme.models.futures_historical.resolve_product",
            new=AsyncMock(return_value=product),
        ),
        patch(
            "openbb_cme.models.futures_historical.fetch_settlements",
            new=AsyncMock(side_effect=settlements),
        ),
        pytest.raises(CMERequestError, match="upstream failed"),
    ):
        run_async(
            CMEFuturesHistoricalFetcher().fetch_data,
            {
                "symbol": "ES",
                "start_date": date(2025, 6, 24),
                "end_date": date(2025, 6, 25),
            },
            {},
        )


def test_options_fetch_fails_atomically_on_one_expiration_error():
    """A failed expiration must not be omitted from an options chain."""
    expirations = [
        {
            "product_id": 138,
            "month_year": "U26",
            "contract_id": contract_id,
            "expiration_date": expiration_date,
            "trade_dates": ["07/22/2026"],
        }
        for contract_id, expiration_date in (
            ("ESU26", date(2026, 9, 18)),
            ("ESZ26", date(2026, 12, 18)),
        )
    ]

    async def settlements(_product_id, _month_year, contract_id, _trade_date, _client):
        if contract_id == "ESZ26":
            raise CMERequestError("expiration failed", url=_URL)
        return [{"strike": "7000", "type": "Call", "settle": "100"}]

    with (
        patch(
            "openbb_cme.models.options_chains.resolve_product",
            new=AsyncMock(return_value={**_PRODUCT, "product_id": 138}),
        ),
        patch(
            "openbb_cme.models.options_chains.fetch_option_expirations",
            new=AsyncMock(return_value=expirations),
        ),
        patch(
            "openbb_cme.models.options_chains.fetch_contract_specifications",
            new=AsyncMock(return_value={"ContractUnit": "$50 x Index"}),
        ),
        patch(
            "openbb_cme.models.options_chains.fetch_option_settlements",
            new=AsyncMock(side_effect=settlements),
        ),
        pytest.raises(CMERequestError, match="expiration failed"),
    ):
        run_async(
            CMEOptionsChainsFetcher().fetch_data,
            {"symbol": "ES", "date": "2026-07-22"},
            {},
        )


def test_settlement_schema_drift_fails_explicitly():
    """A 200 response without a settlements collection is not treated as empty."""
    with (
        patch(
            "openbb_cme.utils.helpers._get_json",
            new=AsyncMock(return_value={"message": "unexpected payload"}),
        ),
        pytest.raises(CMERequestError, match="invalid futures settlement payload"),
    ):
        run_async(fetch_settlements, "ES", date(2026, 7, 22), 133)
