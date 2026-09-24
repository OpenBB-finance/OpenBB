"""Tests for the remaining conditional branches."""

import pytest

from openbb_tmx.utils import curl_session, directory, helpers, quotemedia

CREDS: dict = {}


class TestEmptyResponses:
    """Every model raises when its source returns nothing."""

    @pytest.fixture
    def no_indices(self, monkeypatch):
        """Serve an empty index file."""

        async def fake(url, use_cache=True, **kwargs):
            return {}

        monkeypatch.setattr(helpers, "get_data_from_url", fake)

    @pytest.mark.parametrize(
        "path",
        [
            "openbb_tmx.models.available_indices.TmxAvailableIndicesFetcher",
            "openbb_tmx.models.index_sectors.TmxIndexSectorsFetcher",
            "openbb_tmx.models.index_info.TmxIndexInfoFetcher",
            "openbb_tmx.models.index_documents.TmxIndexDocumentsFetcher",
        ],
    )
    async def test_index_models_raise(self, no_indices, path):
        import importlib

        module, name = path.rsplit(".", 1)
        fetcher = getattr(importlib.import_module(module), name)

        with pytest.raises(Exception):
            await fetcher.fetch_data({"symbol": "^TSX"}, CREDS)

    @pytest.fixture
    def no_etfs(self, monkeypatch):
        """Serve an empty ETF universe."""

        async def fake(use_cache=True):
            return []

        monkeypatch.setattr(helpers, "get_all_etfs", fake)

    @pytest.mark.parametrize(
        "path",
        [
            "openbb_tmx.models.etf_sectors.TmxEtfSectorsFetcher",
            "openbb_tmx.models.etf_countries.TmxEtfCountriesFetcher",
        ],
    )
    async def test_etf_models_raise(self, no_etfs, path):
        import importlib

        module, name = path.rsplit(".", 1)
        fetcher = getattr(importlib.import_module(module), name)

        with pytest.raises(Exception):
            await fetcher.fetch_data({"symbol": "XIU"}, CREDS)

    async def test_calendar_earnings_empty(self, monkeypatch):
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.models.calendar_earnings import TmxCalendarEarningsFetcher

        async def fake(*args, **kwargs):
            return {"getEnhancedEarningsForDate": []}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", fake)

        with pytest.raises(EmptyDataError, match="No earnings were reported"):
            await TmxCalendarEarningsFetcher.fetch_data(
                {"start_date": "2026-07-24", "end_date": "2026-07-24"}, CREDS
            )

    async def test_company_news_empty(self, monkeypatch):
        from openbb_tmx.models.company_news import TmxCompanyNewsFetcher

        async def fake(*args, **kwargs):
            return {"news": None}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", fake)

        assert await TmxCompanyNewsFetcher.fetch_data({"symbol": "AC"}, CREDS) == []

    async def test_company_filings_empty(self, monkeypatch):
        from openbb_tmx.models.company_filings import TmxCompanyFilingsFetcher

        async def fake(*args, **kwargs):
            return {"filings": []}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", fake)

        assert await TmxCompanyFilingsFetcher.fetch_data({"symbol": "AC"}, CREDS) == []

    async def test_price_target_consensus_empty(self, monkeypatch):
        from openbb_tmx.models.price_target_consensus import (
            TmxPriceTargetConsensusFetcher,
        )

        async def fake(*args, **kwargs):
            return {}

        monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", fake)

        assert (
            await TmxPriceTargetConsensusFetcher.fetch_data({"symbol": "AC"}, CREDS)
            == []
        )


class TestOptionsAnalysisLoader:
    """The analysis commands share one chain loader."""

    async def test_loader_delegates_to_the_fetcher(self, monkeypatch):
        from openbb_tmx.routers import options as options_router

        seen: dict = {}

        async def fake(params, creds):
            seen.update(params)
            return "chain"

        monkeypatch.setattr(
            "openbb_tmx.models.options_chains.TmxOptionsChainsFetcher.fetch_data", fake
        )
        assert await options_router._load_chain("AC") == "chain"
        assert seen["symbol"] == "AC"


class TestCurlSessionWarmup:
    """The impersonating session warms up against the site root."""

    @pytest.fixture
    def warmed(self, monkeypatch):
        """Record the URLs a new session is primed against."""
        seen: list = []

        class Session:
            def get(self, url, **kwargs):
                seen.append(url)

        monkeypatch.setattr("curl_cffi.requests.Session", lambda **kw: Session())
        curl_session.get_session.cache_clear()

        yield seen

        curl_session.get_session.cache_clear()

    def test_the_root_is_requested(self, warmed):
        curl_session.get_session("ciro", warmup=True)

        assert warmed == [curl_session.WARMUP_URLS["ciro"]]

    def test_an_unknown_host_has_no_warmup(self, warmed):
        curl_session.get_session("other", warmup=True)

        assert warmed == []

    def test_the_warmup_can_be_skipped(self, warmed):
        curl_session.get_session("ciro", warmup=False)

        assert warmed == []


class TestDirectoryDepth:
    """The sweep stops at the maximum prefix depth."""

    async def test_depth_limit(self, monkeypatch):
        calls: list = []

        async def fake(
            query, limit=100, country=None, symbol_only=False, use_cache=True
        ):
            calls.append(query)
            return [
                {"symbolId": i, "symbol": f"S{i}"} for i in range(directory.ROW_CAP)
            ]

        monkeypatch.setattr(directory, "lookup_symbols", fake)
        results: dict = {}
        await directory._sweep_prefix(
            "a" * directory.MAX_PREFIX_LENGTH, None, results, True
        )
        assert len(calls) == 1


class TestQuoteMediaCacheClear:
    """Token minting is retried after a refusal."""

    async def test_lookup_refreshes_the_token(self, monkeypatch):
        tokens = iter(["stale", "fresh"])
        seen: list = []

        async def mint(tool):
            return next(tokens)

        async def request(url, use_cache=True, **kwargs):
            seen.append(url)
            return [] if "fresh" in url else None

        quotemedia.get_token.cache_clear()
        monkeypatch.setattr(quotemedia, "_mint_token", mint)
        monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", request)
        await directory.lookup_symbols("a")
        assert any("fresh" in u for u in seen)
