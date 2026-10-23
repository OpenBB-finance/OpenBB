"""Tests for the Deribit JSON-RPC transport."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_deribit.utils import client


class _Response:
    """A stand-in for one aiohttp response."""

    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    async def json(self, content_type=None):
        """Return the decoded payload, or raise what a bad body would."""
        if isinstance(self.payload, Exception):
            raise self.payload

        return self.payload


class _Session:
    """A stand-in for one aiohttp session."""

    def __init__(self, response):
        self.response = response
        self.urls: list = []

    async def get(self, url, timeout=None):
        """Record the URL and return the canned response."""
        self.urls.append(url)

        if isinstance(self.response, Exception):
            raise self.response

        return self.response


@pytest.fixture
def transport(monkeypatch):
    """Install a canned session and return it."""

    def install(response, cached=True):
        session = _Session(response)

        async def _get_session():
            return session

        monkeypatch.setattr("openbb_deribit.utils.session.get_session", _get_session)
        monkeypatch.setattr(
            "openbb_deribit.utils.session.get_cached_session", _get_session
        )

        return session

    return install


class TestBuildUrl:
    """``build_url`` writes the query the exchange expects."""

    def test_no_params(self):
        """A method with no parameters carries no query string."""
        assert client.build_url("get_currencies") == (
            "https://www.deribit.com/api/v2/public/get_currencies"
        )

    def test_drops_none(self):
        """A parameter left unset is not sent."""
        url = client.build_url("get_instruments", {"currency": "BTC", "kind": None})

        assert url.endswith("get_instruments?currency=BTC")

    def test_lowercases_booleans(self):
        """A boolean is sent as the lower-case literal the exchange reads."""
        url = client.build_url("get_instruments", {"expired": True})

        assert url.endswith("get_instruments?expired=true")

    def test_encodes_values(self):
        """A value needing escaping is percent-encoded."""
        url = client.build_url("ticker", {"instrument_name": "BTC-25DEC26-90000-C"})

        assert "instrument_name=BTC-25DEC26-90000-C" in url

    def test_empty_params_mapping(self):
        """An empty mapping is the same as none at all."""
        assert client.build_url("status", {}) == client.build_url("status")


class TestRequest:
    """``request`` unwraps the JSON-RPC envelope and reports failures."""

    @pytest.mark.asyncio
    async def test_returns_result(self, transport):
        """A successful call returns the result member."""
        session = transport(_Response({"jsonrpc": "2.0", "result": [1, 2]}))

        assert await client.request("get_currencies") == [1, 2]
        assert session.urls == ["https://www.deribit.com/api/v2/public/get_currencies"]

    @pytest.mark.asyncio
    async def test_uncached_path(self, transport):
        """Passing ``use_cache=False`` still returns the result."""
        transport(_Response({"result": {"locked": "false"}}))

        assert await client.request("status", use_cache=False) == {"locked": "false"}

    @pytest.mark.asyncio
    async def test_missing_result(self, transport):
        """A payload with no result member returns None rather than raising."""
        transport(_Response({"jsonrpc": "2.0"}))

        assert await client.request("get_time") is None

    @pytest.mark.asyncio
    async def test_json_rpc_error(self, transport):
        """A JSON-RPC error is raised with its message and reason."""
        transport(
            _Response(
                {
                    "error": {
                        "message": "Invalid params",
                        "data": {"reason": "invalid currency"},
                    }
                }
            )
        )

        with pytest.raises(OpenBBError, match="invalid currency"):
            await client.request("get_instruments", {"currency": "XYZ"})

    @pytest.mark.asyncio
    async def test_json_rpc_error_without_data(self, transport):
        """An error carrying no data still names its message."""
        transport(_Response({"error": {"message": "not_supported"}}))

        with pytest.raises(OpenBBError, match="not_supported"):
            await client.request("get_last_trades_by_currency")

    @pytest.mark.asyncio
    async def test_json_rpc_error_as_string(self, transport):
        """An error the exchange sends as a bare string is reported as-is."""
        transport(_Response({"error": "rate_limited"}))

        with pytest.raises(OpenBBError, match="rate_limited"):
            await client.request("ticker")

    @pytest.mark.asyncio
    async def test_non_dict_payload(self, transport):
        """A body that is not an object is rejected."""
        transport(_Response([1, 2, 3]))

        with pytest.raises(OpenBBError, match="Unexpected Deribit response"):
            await client.request("get_time")

    @pytest.mark.asyncio
    async def test_rate_limited(self, transport):
        """A 429 names the status and says what to do about it."""
        transport(_Response(None, status=429))

        with pytest.raises(OpenBBError, match="HTTP 429"):
            await client.request("get_order_book")

    @pytest.mark.asyncio
    async def test_other_bad_status(self, transport):
        """Any other non-200 names its status."""
        transport(_Response(None, status=503))

        with pytest.raises(OpenBBError, match="HTTP 503"):
            await client.request("status")

    @pytest.mark.asyncio
    async def test_transport_failure(self, transport):
        """A transport failure is wrapped, naming the method."""
        transport(TimeoutError("timed out"))

        with pytest.raises(OpenBBError, match="public/ticker"):
            await client.request("ticker")

    @pytest.mark.asyncio
    async def test_undecodable_body(self, transport):
        """A body that cannot be decoded is wrapped."""
        transport(_Response(ValueError("not json")))

        with pytest.raises(OpenBBError, match="ValueError"):
            await client.request("get_time")


class TestGather:
    """``gather`` runs several calls and keeps the failures in place."""

    @pytest.mark.asyncio
    async def test_returns_in_order(self, monkeypatch):
        """Results come back in the order the calls were given."""

        async def _request(method, params=None, use_cache=True):
            return params["n"]

        monkeypatch.setattr(client, "request", _request)
        results = await client.gather(
            [("ticker", {"n": 1}), ("ticker", {"n": 2}), ("ticker", {"n": 3})]
        )

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_keeps_exceptions(self, monkeypatch):
        """A call that fails leaves its exception in place of a result."""

        async def _request(method, params=None, use_cache=True):
            if params["n"] == 2:
                raise OpenBBError("no")

            return params["n"]

        monkeypatch.setattr(client, "request", _request)
        results = await client.gather(
            [("ticker", {"n": 1}), ("ticker", {"n": 2})], use_cache=False
        )

        assert results[0] == 1
        assert isinstance(results[1], OpenBBError)
