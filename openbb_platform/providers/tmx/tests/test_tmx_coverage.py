"""Tests for the remaining transport and router paths."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.utils import cache, helpers, mx

OPTIONS_LIST_HTML = """
<table>
<tr><th>Option Symbol</th><th>Underlying Symbol</th><th>Name of Company</th></tr>
<tr><td>AC</td><td>AC</td><td>Air Canada</td></tr>
<tr><td>BNS</td><td>BNS</td><td>Bank of Nova Scotia</td></tr>
</table>
"""

QUOTES_HTML = """
<table>
<tr><th colspan="7">Calls</th><th>Unnamed: 7_level_0</th><th colspan="7">Puts</th></tr>
</table>
"""

EOD_CSV = (
    "Date,Symbol,Class Symbol,Root Symbol,Underlying Symbol,Ins. Type,Strike,"
    "Expiry date,Call/Put,Bid,Ask,Bid size,Ask size,Last price,Volume,"
    "Previous price,Net change,Open,High,Low,Total value,Nb. of transaction,"
    "Settlement price,Open interest,Implied volatility\n"
    "2026-07-24,AC,AC,AC,AC,O,20.0,2026-07-31,0,2.9,3.1,10,10,3.0,5,2.8,0.2,"
    "2.9,3.2,2.8,1500,3,3.0,100,40.0\n"
)


class TestCacheRequests:
    """The cached and uncached URL transports."""

    async def test_cached_request_reads_json(self, monkeypatch):
        class Response:
            async def json(self, content_type=None):
                return {"ok": True}

            def release(self):
                return None

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def request(self, method, url, **kwargs):
                return Response()

        monkeypatch.setattr(
            "aiohttp_client_cache.session.CachedSession", lambda **kw: Session()
        )
        assert await cache.amake_request("https://x") == {"ok": True}

    async def test_uncached_request_reads_text(self, monkeypatch):
        class Response:
            async def text(self):
                return "hello"

            def release(self):
                return None

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def request(self, method, url, **kwargs):
                return Response()

        monkeypatch.setattr("aiohttp.ClientSession", lambda **kw: Session())
        body = await cache.amake_request(
            "https://x", use_cache=False, accept_type="text"
        )
        assert body == "hello"

    async def test_binary_read(self, monkeypatch):
        class Response:
            async def read(self):
                return b"\x00"

            def release(self):
                return None

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def request(self, method, url, **kwargs):
                return Response()

        monkeypatch.setattr("aiohttp.ClientSession", lambda **kw: Session())
        assert (
            await cache.amake_request(
                "https://x", use_cache=False, accept_type="binary"
            )
            == b"\x00"
        )

    def test_release_tolerates_a_cached_response(self):
        cache._release(object())

    async def test_gql_without_cache(self, monkeypatch):
        class Response:
            async def json(self, content_type=None):
                return {"data": {"ok": 1}}

            def release(self):
                return None

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def post(self, *args, **kwargs):
                return Response()

        monkeypatch.setattr("aiohttp.ClientSession", lambda **kw: Session())
        assert await cache.amake_gql_request("op", "q", use_cache=False) == {"ok": 1}


class TestMxUniverse:
    """The Montreal Exchange universe."""

    @pytest.fixture(autouse=True)
    def _no_enrichment(self, monkeypatch):
        """Serve empty listing metadata so the parse is tested in isolation."""

        async def empty(use_cache=True):
            return {}

        monkeypatch.setattr(mx, "get_options_listings", empty)
        monkeypatch.setattr(mx, "get_expiry_cycles", empty)

    async def test_universe_is_parsed(self, monkeypatch):
        async def fake(url, use_cache=True, accept_type="json", **kwargs):
            return (
                '<select name="symbol" id="symbolIRD">'
                '<option value="CGB*">CGB</option></select>'
            )

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        mx.get_instrument_universe.cache_clear()
        rows = await mx.get_instrument_universe()
        assert rows[0]["symbol"] == "CGB"

    async def test_empty_page_raises(self, monkeypatch):
        async def fake(url, **kwargs):
            return ""

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        mx.get_instrument_universe.cache_clear()

        with pytest.raises(OpenBBError, match="came back empty"):
            await mx.get_instrument_universe()

    async def test_filter_by_class(self, monkeypatch):
        async def fake(url, **kwargs):
            return (
                '<select name="symbol" id="symbolIRD">'
                '<option value="CGB*">CGB</option></select>'
                '<select name="symbol" id="symbolOEQ">'
                '<option value="AC*">AC</option></select>'
            )

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        mx.get_instrument_universe.cache_clear()
        assert len(await mx.get_instruments_by_class()) == 2
        mx.get_instrument_universe.cache_clear()
        rows = await mx.get_instruments_by_class("interest_rate_derivative")
        assert [r["symbol"] for r in rows] == ["CGB"]


class TestOptionsHelpers:
    """The Montreal Exchange option helpers."""

    async def test_options_tickers(self, monkeypatch):
        async def fake(url, use_cache=True, **kwargs):
            return OPTIONS_LIST_HTML

        monkeypatch.setattr(helpers, "get_data_from_url", fake)
        frame = await helpers.get_all_options_tickers()
        assert "AC" in frame.index

    async def test_options_tickers_empty(self, monkeypatch):
        async def fake(url, use_cache=True, **kwargs):
            return None

        monkeypatch.setattr(helpers, "get_data_from_url", fake)

        with pytest.raises(OpenBBError, match="Error with the request"):
            await helpers.get_all_options_tickers()

    async def test_eod_chains(self, monkeypatch):
        from pandas import DataFrame

        async def tickers(use_cache=True):
            return DataFrame(
                [{"underlying_symbol": "AC", "company": "Air Canada"}], index=["AC"]
            ).rename_axis("option_symbol")

        async def fake(url, use_cache=True, **kwargs):
            return EOD_CSV

        monkeypatch.setattr(helpers, "get_all_options_tickers", tickers)
        monkeypatch.setattr(helpers, "get_data_from_url", fake)
        frame = await helpers.download_eod_chains("AC", date(2026, 7, 24))
        assert not frame.empty
        assert frame["option_type"].iloc[0] == "call"

    async def test_eod_chains_rejects_unlisted(self, monkeypatch):
        from pandas import DataFrame

        async def tickers(use_cache=True):
            return DataFrame(
                [{"underlying_symbol": "BNS", "company": "Bank"}], index=["BNS"]
            ).rename_axis("option_symbol")

        monkeypatch.setattr(helpers, "get_all_options_tickers", tickers)

        with pytest.raises(OpenBBError, match="not a valid listing"):
            await helpers.download_eod_chains("ZZZZ")

    async def test_eod_chains_empty_download(self, monkeypatch):
        from pandas import DataFrame

        async def tickers(use_cache=True):
            return DataFrame(
                [{"underlying_symbol": "AC", "company": "Air Canada"}], index=["AC"]
            ).rename_axis("option_symbol")

        async def fake(url, use_cache=True, **kwargs):
            return None

        monkeypatch.setattr(helpers, "get_all_options_tickers", tickers)
        monkeypatch.setattr(helpers, "get_data_from_url", fake)

        with pytest.raises(OpenBBError, match="no data was returned"):
            await helpers.download_eod_chains("AC")
