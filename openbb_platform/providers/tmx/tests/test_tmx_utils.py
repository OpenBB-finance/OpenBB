"""Tests for the TMX transport, directory, and vendor helpers."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_tmx.utils import cache, ciro, curl_session, directory, quotemedia


class TestCacheBackend:
    """The shared on-disk cache."""

    def test_backend_allows_get_and_post(self):
        backend = cache.get_cache_backend()
        assert "GET" in backend.allowed_methods
        assert "POST" in backend.allowed_methods

    def test_random_agent(self):
        assert cache.get_random_agent()


class TestGqlTransport:
    """The GraphQL transport."""

    async def test_returns_the_data_member(self, monkeypatch):
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

        monkeypatch.setattr(
            "aiohttp_client_cache.session.CachedSession", lambda **kw: Session()
        )
        data = await cache.amake_gql_request("op", "query {}", {})
        assert data == {"ok": 1}

    async def test_raises_on_graphql_errors(self, monkeypatch):
        class Response:
            async def json(self, content_type=None):
                return {"errors": [{"message": "boom"}]}

            def release(self):
                return None

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def post(self, *args, **kwargs):
                return Response()

        monkeypatch.setattr(
            "aiohttp_client_cache.session.CachedSession", lambda **kw: Session()
        )

        with pytest.raises(OpenBBError, match="boom"):
            await cache.amake_gql_request("op", "query {}", {})

    async def test_raises_on_unexpected_shape(self, monkeypatch):
        class Response:
            async def json(self, content_type=None):
                return "not json"

            def release(self):
                return None

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def post(self, *args, **kwargs):
                return Response()

        monkeypatch.setattr(
            "aiohttp_client_cache.session.CachedSession", lambda **kw: Session()
        )

        with pytest.raises(OpenBBError, match="Unexpected TMX response"):
            await cache.amake_gql_request("op", "query {}", {})


class TestQuoteMediaTokens:
    """Datatool token minting."""

    async def test_token_is_minted_and_cached(self, monkeypatch):
        calls: list = []

        async def fake(tool):
            calls.append(tool)
            return "tok"

        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", fake)
        assert await quotemedia.get_token("options") == "tok"
        assert await quotemedia.get_token("options") == "tok"
        assert len(calls) == 1

    async def test_declined_token(self, monkeypatch):
        class Response:
            async def json(self, content_type=None):
                return {}

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

        with pytest.raises(OpenBBError, match="did not authorize"):
            await quotemedia._mint_token("options")

    def test_screener_session_id_is_a_digest(self):
        assert len(quotemedia.SCREENER_TOOL) == 64
        assert all(c in "0123456789abcdef" for c in quotemedia.SCREENER_TOOL)


class TestQuoteMediaEndpoints:
    """The datatool wrappers."""

    async def test_datatool_requires_results(self, monkeypatch):
        async def fake(url, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", lambda tool: _tok())

        with pytest.raises(OpenBBError, match="No QuoteMedia results"):
            await quotemedia.get_datatool("x.json", "options")

    async def test_option_chain_replays_the_expiry_list(self, monkeypatch):
        seen: list = []

        async def fake(endpoint, tool, use_cache=True, **params):
            seen.append(params)

            if "expiryDates" in params:
                return {"expiryGroup": [1, 2, 3]}

            return {
                "expiryDates": {
                    "expiryDate": [{"date": "2026-07-31"}, {"date": "2026-08-07"}]
                },
                "expiryGroup": [1],
            }

        monkeypatch.setattr(quotemedia, "get_datatool", fake)
        results = await quotemedia.get_option_chain("AC")
        assert len(results["expiryGroup"]) == 3
        assert "expiryDates" in seen[-1]

    async def test_option_chain_skips_the_replay_when_complete(self, monkeypatch):
        async def fake(endpoint, tool, use_cache=True, **params):
            return {
                "expiryDates": {"expiryDate": [{"date": "2026-07-31"}]},
                "expiryGroup": [1],
            }

        monkeypatch.setattr(quotemedia, "get_datatool", fake)
        results = await quotemedia.get_option_chain("AC")
        assert len(results["expiryGroup"]) == 1

    async def test_financials_wraps_a_single_report(self, monkeypatch):
        async def fake(endpoint, tool, use_cache=True, **params):
            return {"Company": {"Report": {"reportYear": 2025}}}

        monkeypatch.setattr(quotemedia, "get_datatool", fake)
        assert await quotemedia.get_financials("AC") == [{"reportYear": 2025}]

    async def test_screener_equities_batches_and_flattens(self, monkeypatch):
        async def fake(url, **kwargs):
            return {
                "results": {
                    "equities": [
                        {
                            "companyBasics": {"symbol": "RY", "name": "Royal Bank"},
                            "keyRatios": {"peRatio": 21.0},
                        }
                    ]
                }
            }

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", lambda tool: _tok())
        rows = await quotemedia.get_screener_equities(["RY"])
        assert rows[0]["symbol"] == "RY"
        assert rows[0]["peRatio"] == 21.0


async def _tok():
    """Return a stub token."""
    return "tok"


class TestDirectory:
    """The instrument symbology sweep."""

    async def test_empty_query_short_circuits(self):
        assert await directory.lookup_symbols("") == []

    @pytest.fixture
    def listed(self, monkeypatch):
        """Serve a directory carrying alternate venue listings."""
        from pandas import DataFrame

        async def frame(
            country=None, symbol_types=None, exchanges=None, use_cache=True
        ):
            return DataFrame(
                [
                    {"symbol": "AC", "marketCap": 8e9, "name": "Air Canada"},
                    {"symbol": "AC:APH", "marketCap": 8e9, "name": "Air Canada"},
                    {"symbol": "RY", "marketCap": 4e11, "name": "Royal Bank"},
                    {"symbol": "TINY", "marketCap": 1e6, "name": "Tiny Co"},
                ]
            )

        monkeypatch.setattr(directory, "get_directory_frame", frame)

    async def test_browsing_lists_the_largest_first(self, listed):
        listing = await directory.browse_symbols()

        assert [row["symbol"] for row in listing] == ["RY", "AC", "TINY"]

    async def test_browsing_leaves_out_alternate_venue_listings(self, listed):
        listing = await directory.browse_symbols()

        assert all(":" not in row["symbol"] for row in listing)

    async def test_browsing_is_capped(self, listed):
        assert len(await directory.browse_symbols(limit=2)) == 2

    async def test_browsing_an_empty_directory_lists_nothing(self, monkeypatch):
        from pandas import DataFrame

        async def nothing(**kwargs):
            return DataFrame()

        monkeypatch.setattr(directory, "get_directory_frame", nothing)

        assert await directory.browse_symbols() == []

    async def test_lookup_retries_then_gives_up(self, monkeypatch):
        attempts: list = []

        async def fake(url, **kwargs):
            attempts.append(url)

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)
        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", lambda tool: _tok())
        assert await directory.lookup_symbols("a") == []
        assert len(attempts) == 2

    async def test_sweep_dedupes_by_symbol_id(self, monkeypatch):
        async def fake(
            query, limit=100, country=None, symbol_only=False, use_cache=True
        ):
            return [
                {
                    "symbolId": 1,
                    "symbol": "AC",
                    "symbolType": "Equity",
                    "exchangeShortName": "TSX",
                    "marketCap": 1.0,
                }
            ]

        monkeypatch.setattr(directory, "lookup_symbols", fake)
        directory.get_master_directory.cache_clear()
        rows = await directory.get_master_directory("CA")
        assert len(rows) == 1

    async def test_empty_directory_raises(self, monkeypatch):
        async def fake(query, **kwargs):
            return []

        monkeypatch.setattr(directory, "lookup_symbols", fake)
        directory.get_master_directory.cache_clear()

        with pytest.raises(OpenBBError, match="came back empty"):
            await directory.get_master_directory("ZZ")

    async def test_frame_filters(self, monkeypatch):
        async def fake(query, **kwargs):
            return [
                {
                    "symbolId": 1,
                    "symbol": "AC",
                    "symbolType": "Equity",
                    "exchangeShortName": "TSX",
                    "marketCap": 1.0,
                },
                {
                    "symbolId": 2,
                    "symbol": "XIU",
                    "symbolType": "ETF",
                    "exchangeShortName": "TSX",
                    "marketCap": 2.0,
                },
            ]

        monkeypatch.setattr(directory, "lookup_symbols", fake)
        directory.get_master_directory.cache_clear()
        frame = await directory.get_directory_frame("CA", symbol_types=["ETF"])
        assert list(frame["symbol"]) == ["XIU"]
        directory.get_master_directory.cache_clear()
        frame = await directory.get_directory_frame("CA", exchanges=["NYSE"])
        assert frame.empty


class TestCurlSession:
    """The Cloudflare-capable session."""

    def test_session_is_cached_per_key(self, monkeypatch):
        made: list = []

        class Session:
            def get(self, *args, **kwargs):
                return None

        def factory(**kwargs):
            made.append(kwargs)
            return Session()

        monkeypatch.setattr("curl_cffi.requests.Session", factory)
        curl_session.get_session.cache_clear()
        curl_session.get_session("other", warmup=False)
        curl_session.get_session("other", warmup=False)
        assert len(made) == 1


class TestCiro:
    """The CIRO debt endpoints."""

    async def test_issuers_and_securities(self, monkeypatch):
        async def fake(key, url, **kwargs):
            return ["ISSUER"] if "issuers" in url else ["CUSIP"]

        monkeypatch.setattr("openbb_tmx.utils.curl_session.get_json", fake)
        assert await ciro.get_issuers() == ["ISSUER"]
        assert await ciro.get_security_ids() == ["CUSIP"]

    async def test_bond_trades_concatenate_windows(self, monkeypatch):
        from datetime import date

        async def fake(path, payload):
            return {"txnData": [{"execDate": payload["from"], "execTime": "10:00"}]}

        monkeypatch.setattr(ciro, "_post_json", fake)
        trades = await ciro.get_bond_trades("1", date(2024, 1, 1), date(2024, 12, 31))
        assert len(trades) == len(ciro._windows(date(2024, 1, 1), date(2024, 12, 31)))


class TestNormalizeUrl:
    """A website is published as a link the browser can follow."""

    def test_a_scheme_is_added_when_the_source_leaves_one_off(self):
        from openbb_tmx.utils.helpers import normalize_url

        assert normalize_url("www.ishares.com") == "https://www.ishares.com"

    def test_a_protocol_relative_url_is_given_a_scheme(self):
        from openbb_tmx.utils.helpers import normalize_url

        assert normalize_url("//cdn.example.com/a") == "https://cdn.example.com/a"

    @pytest.mark.parametrize(
        "url", ["https://www.rbc.com", "http://x.ca", "ftp://files.example.com"]
    )
    def test_an_absolute_url_is_left_alone(self, url):
        from openbb_tmx.utils.helpers import normalize_url

        assert normalize_url(url) == url

    @pytest.mark.parametrize("absent", ["", "  ", "nan", "N/A", "none", "-", None])
    def test_an_absent_website_is_nothing(self, absent):
        from openbb_tmx.utils.helpers import normalize_url

        assert normalize_url(absent) is None


class TestPurgeNulls:
    """Every absent value leaves the frame as None."""

    def test_a_missing_string_does_not_survive_as_a_float(self):
        """The source leaves a NaN where a fund declares no frequency."""
        from pandas import DataFrame

        from openbb_tmx.utils.helpers import purge_nulls

        purged = purge_nulls(DataFrame({"a": ["Monthly", None]}))

        assert purged["a"][1] is None

    def test_the_source_placeholders_are_purged(self):
        from pandas import DataFrame

        from openbb_tmx.utils.helpers import purge_nulls

        purged = purge_nulls(DataFrame({"a": ["N/A", "-", "", "kept"]}))

        assert purged["a"].tolist() == [None, None, None, "kept"]

    def test_a_number_is_left_alone(self):
        from pandas import DataFrame

        from openbb_tmx.utils.helpers import purge_nulls

        purged = purge_nulls(DataFrame({"a": [1.5, None]}))

        assert purged["a"][0] == 1.5
        assert purged["a"][1] is None
