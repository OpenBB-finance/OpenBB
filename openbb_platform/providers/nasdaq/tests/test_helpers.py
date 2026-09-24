"""Tests for openbb_nasdaq.utils.helpers."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_nasdaq.utils import helpers


class TestTextHelpers:
    """Cover the string and header helpers."""

    def test_remove_html_tags(self):
        """Tags are replaced by spaces."""
        assert helpers.remove_html_tags("<b>Net</b> Income") == " Net  Income"

    def test_get_random_agent(self, monkeypatch):
        """The agent chosen by the underlying library is returned unchanged."""

        class _UserAgent:
            def __init__(self, limit=100):
                pass

            def get_random_user_agent(self):
                """Return a fixed agent for the test."""
                return "Mozilla/5.0 (Test Suite)"

        monkeypatch.setattr("random_user_agent.user_agent.UserAgent", _UserAgent)

        assert helpers.get_random_agent() == "Mozilla/5.0 (Test Suite)"

    @pytest.mark.parametrize("accept", ["json", "text", "pdf"])
    def test_get_headers_accepts_every_type(self, accept):
        """Each supported accept type builds a header set."""
        headers = helpers.get_headers(accept)

        assert "User-Agent" in headers
        assert "Accept" in headers

    def test_get_headers_json_carries_origin(self):
        """The JSON headers carry the browser origin the API requires."""
        assert helpers.get_headers("json")["Origin"] == "https://www.nasdaq.com"

    def test_get_headers_rejects_unknown_type(self):
        """An unsupported accept type is refused."""
        with pytest.raises(ValueError, match="Invalid accept_type"):
            helpers.get_headers("xml")


class TestCoercion:
    """Cover the display-string coercers."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("$1,234.50", "1234.50"),
            ("(500)", "-500"),
            ("N/A", None),
            ("--", None),
            ("", None),
            ("NM", None),
            (None, None),
            (12, 12),
        ],
    )
    def test_clean_value(self, value, expected):
        """Placeholders become None and decorations are stripped."""
        assert helpers.clean_value(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("$1,234.50", 1234.5), ("(500)", -500.0), ("N/A", None), ("abc", None)],
    )
    def test_to_number(self, value, expected):
        """Numbers are parsed and unparseable cells become None."""
        assert helpers.to_number(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"), [("+3.53%", 0.0353), ("-1.5%", -0.015), ("N/A", None)]
    )
    def test_to_percent(self, value, expected):
        """Percentages are normalized to fractions."""
        assert helpers.to_percent(value) == pytest.approx(expected)

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("07/24/2026", date(2026, 7, 24)),
            ("Jul 24, 2026", date(2026, 7, 24)),
            (date(2026, 7, 24), date(2026, 7, 24)),
            ("N/A", None),
            ("", None),
            (None, None),
            ("not a date", None),
        ],
    )
    def test_to_date(self, value, expected):
        """Every Nasdaq date format parses, and placeholders become None."""
        assert helpers.to_date(value) == expected


class TestDateRange:
    """Cover the inclusive date generator."""

    def test_yields_every_day_inclusive(self):
        """Both endpoints are included."""
        days = list(helpers.date_range(date(2026, 1, 1), date(2026, 1, 3)))

        assert days == [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]


class TestRowsFromTable:
    """Cover the table-envelope unwrapping."""

    def test_flat_rows(self):
        """Rows directly on the object are returned."""
        assert helpers.rows_from_table({"rows": [{"a": 1}]}) == [{"a": 1}]

    def test_nested_rows(self):
        """Rows nested one level under 'table' are returned."""
        assert helpers.rows_from_table({"table": {"rows": [{"a": 1}]}}) == [{"a": 1}]

    @pytest.mark.parametrize("table", [None, "text", {}, {"table": {}}])
    def test_missing_rows(self, table):
        """Anything without rows yields an empty list."""
        assert helpers.rows_from_table(table) == []


class TestDirectory:
    """Cover the symbol directory download and parsing."""

    def test_parse_directory_drops_creation_line(self, directory_text):
        """The trailing file-creation row is removed."""
        frame = helpers.parse_directory(directory_text)

        assert len(frame) == 3
        assert "ZTEST" in frame["Symbol"].tolist()

    def test_get_nasdaq_directory(self, monkeypatch, directory_text):
        """The directory file is returned as text."""

        class _Response:
            text = directory_text

            def raise_for_status(self):
                """Accept the response."""

        monkeypatch.setattr(
            helpers, "make_request", lambda *a, **k: _Response(), raising=False
        )
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _Response(),
        )

        assert "AAPL" in helpers.get_nasdaq_directory("nasdaqtraded")

    def test_get_nasdaq_directory_raises(self, monkeypatch):
        """A failed download is reported as an OpenBBError."""

        def _boom(*args, **kwargs):
            raise RuntimeError("offline")

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _boom)

        with pytest.raises(OpenBBError, match="Failed to download"):
            helpers.get_nasdaq_directory("otherlisted")

    def test_directory_index_maps_asset_class(self, monkeypatch, directory_text):
        """Non-test issues are indexed as stocks or ETFs."""
        monkeypatch.setattr(helpers, "get_nasdaq_directory", lambda *a: directory_text)

        index = helpers._directory_index()

        assert index["AAPL"] == "stocks"
        assert index["QQQ"] == "etf"

    def test_directory_index_survives_failure(self, monkeypatch):
        """An unreachable directory yields an empty index rather than raising."""

        def _boom(*args, **kwargs):
            raise OpenBBError("offline")

        monkeypatch.setattr(helpers, "get_nasdaq_directory", _boom)

        assert helpers._directory_index() == {}

    def test_directory_asset_class_unknown_symbol(self, monkeypatch):
        """A symbol outside the directory resolves to None."""
        monkeypatch.setattr(helpers, "_directory_index", lambda: {"AAPL": "stocks"})

        assert helpers._directory_asset_class("NOPE") is None


class TestResolveAssetClass:
    """Cover asset-class resolution."""

    def test_directory_hit_avoids_the_network(self, monkeypatch):
        """A symbol in the listing directory is resolved without a request."""
        monkeypatch.setattr(helpers, "_directory_asset_class", lambda s: "etf")

        async def _fail(*args, **kwargs):
            raise AssertionError("the directory hit should short-circuit")

        monkeypatch.setattr(helpers, "get_nasdaq_data", _fail)

        assert asyncio.run(helpers.resolve_asset_class("QQQ")) == "etf"

    def test_probes_until_a_class_answers(self, monkeypatch):
        """Symbols outside the directory are probed in order."""
        monkeypatch.setattr(helpers, "_directory_asset_class", lambda s: None)
        seen: list[str] = []

        async def _probe(path, **kwargs):
            seen.append(path)

            if "index" not in path:
                raise OpenBBError("no such symbol")

            return {}

        monkeypatch.setattr(helpers, "get_nasdaq_data", _probe)

        assert asyncio.run(helpers.resolve_asset_class("COMP")) == "index"
        assert len(seen) == 3

    def test_falls_back_to_stocks(self, monkeypatch):
        """A symbol no class claims defaults to stocks."""
        monkeypatch.setattr(helpers, "_directory_asset_class", lambda s: None)

        async def _boom(*args, **kwargs):
            raise OpenBBError("nope")

        monkeypatch.setattr(helpers, "get_nasdaq_data", _boom)

        assert asyncio.run(helpers.resolve_asset_class("ZZZZ")) == "stocks"


class TestGetNasdaqData:
    """Cover the response envelope handling."""

    def test_returns_the_data_member(self, monkeypatch):
        """A 200 envelope yields its data member."""

        async def _request(url, **kwargs):
            return {"status": {"rCode": 200}, "data": {"ok": True}}

        monkeypatch.setattr(helpers, "_cached_request", _request)

        assert asyncio.run(helpers.get_nasdaq_data("market-info")) == {"ok": True}

    def test_bypasses_the_cache(self, monkeypatch):
        """use_cache=False routes to the live request path."""
        called: list[str] = []

        async def _live(url, **kwargs):
            called.append(url)

            return {"status": {"rCode": 200}, "data": []}

        async def _cached(url, **kwargs):
            raise AssertionError("the cache should be bypassed")

        monkeypatch.setattr(helpers, "_live_request", _live)
        monkeypatch.setattr(helpers, "_cached_request", _cached)
        asyncio.run(helpers.get_nasdaq_data("market-info", use_cache=False))

        assert called and called[0].endswith("/market-info")

    def test_rejects_a_non_dict_response(self, monkeypatch):
        """A malformed response is reported."""

        async def _request(url, **kwargs):
            return "<html>"

        monkeypatch.setattr(helpers, "_cached_request", _request)

        with pytest.raises(OpenBBError, match="Unexpected Nasdaq response"):
            asyncio.run(helpers.get_nasdaq_data("market-info"))

    def test_surfaces_the_error_message(self, monkeypatch):
        """A non-200 envelope raises with the upstream detail."""

        async def _request(url, **kwargs):
            return {
                "status": {
                    "rCode": 400,
                    "bCodeMessage": [{"errorMessage": "Invalid value"}],
                }
            }

        monkeypatch.setattr(helpers, "_cached_request", _request)

        with pytest.raises(OpenBBError, match="Invalid value"):
            asyncio.run(helpers.get_nasdaq_data("screener/shares"))

    def test_handles_a_missing_error_message(self, monkeypatch):
        """A non-200 envelope without detail still raises."""

        async def _request(url, **kwargs):
            return {"status": {"rCode": 500}}

        monkeypatch.setattr(helpers, "_cached_request", _request)

        with pytest.raises(OpenBBError, match="failed"):
            asyncio.run(helpers.get_nasdaq_data("market-info"))


class TestCacheBackend:
    """Cover the on-disk cache construction."""

    def test_builds_a_sqlite_backend(self):
        """The backend carries the per-endpoint TTL table."""
        backend = helpers.get_cache_backend()

        assert backend.expire_after == helpers.CACHE_TTL_DEFAULT
        assert backend.urls_expire_after == helpers.URL_CACHE_TTL


class TestHistoricalPrices:
    """Cover the price history helpers."""

    @staticmethod
    def _payload():
        """Return a two-session trades table."""
        return {
            "tradesTable": {
                "rows": [
                    {
                        "date": "07/24/2026",
                        "open": "$1.00",
                        "high": "$2.00",
                        "low": "$0.50",
                        "close": "$1.50",
                        "volume": "1,000",
                    },
                    {
                        "date": "N/A",
                        "open": "",
                        "high": "",
                        "low": "",
                        "close": "",
                        "volume": "",
                    },
                ]
            }
        }

    def test_parses_and_sorts(self, monkeypatch):
        """Undated rows are dropped and the rest are sorted by session."""

        async def _data(path, **kwargs):
            return self._payload()

        monkeypatch.setattr(helpers, "get_nasdaq_data", _data)
        rows = asyncio.run(helpers.get_historical_prices("AAPL", "stocks"))

        assert len(rows) == 1
        assert rows[0]["close"] == 1.5

    def test_raises_when_empty(self, monkeypatch):
        """A symbol with no sessions is reported."""

        async def _data(path, **kwargs):
            return {"tradesTable": {"rows": []}}

        monkeypatch.setattr(helpers, "get_nasdaq_data", _data)

        with pytest.raises(EmptyDataError, match="No historical prices"):
            asyncio.run(helpers.get_historical_prices("AAPL", "stocks"))

    def test_gather_labels_only_multi_symbol(self, monkeypatch):
        """The symbol column appears only when more than one is requested."""

        async def _one(symbol, asset_class, start, end):
            return [{"date": date(2026, 7, 24), "close": 1.0}]

        monkeypatch.setattr(helpers, "get_historical_prices", _one)
        single = asyncio.run(helpers.gather_historical_prices("AAPL", "stocks"))
        multi = asyncio.run(helpers.gather_historical_prices("AAPL,MSFT", "stocks"))

        assert "symbol" not in single[0]
        assert {r["symbol"] for r in multi} == {"AAPL", "MSFT"}

    def test_gather_resolves_asset_class(self, monkeypatch):
        """The asset class is resolved per symbol when not supplied."""
        seen: list[str] = []

        async def _resolve(symbol):
            seen.append(symbol)

            return "etf"

        async def _one(symbol, asset_class, start, end):
            assert asset_class == "etf"

            return [{"date": date(2026, 7, 24), "close": 1.0}]

        monkeypatch.setattr(helpers, "resolve_asset_class", _resolve)
        monkeypatch.setattr(helpers, "get_historical_prices", _one)
        asyncio.run(helpers.gather_historical_prices("QQQ"))

        assert seen == ["QQQ"]

    def test_gather_warns_and_continues(self, monkeypatch):
        """One failing symbol warns without sinking the request."""

        async def _one(symbol, asset_class, start, end):
            if symbol == "BAD":
                raise OpenBBError("no data")

            return [{"date": date(2026, 7, 24), "close": 1.0}]

        monkeypatch.setattr(helpers, "get_historical_prices", _one)

        with pytest.warns(UserWarning, match="BAD"):
            rows = asyncio.run(helpers.gather_historical_prices("AAPL,BAD", "stocks"))

        assert len(rows) == 1

    def test_gather_raises_when_all_fail(self, monkeypatch):
        """No symbol returning history is an error."""

        async def _one(symbol, asset_class, start, end):
            raise OpenBBError("no data")

        monkeypatch.setattr(helpers, "get_historical_prices", _one)

        with pytest.warns(UserWarning), pytest.raises(EmptyDataError):
            asyncio.run(helpers.gather_historical_prices("AAPL,MSFT", "stocks"))


class TestBasicQuotes:
    """Cover the batch quote helper."""

    def test_orders_by_request(self, monkeypatch):
        """Records are returned in the order the symbols were requested."""

        async def _resolve(symbol):
            return "stocks"

        async def _data(path, **kwargs):
            return {
                "records": [
                    {"key": "MSFT|STOCKS", "lastSale": "$2"},
                    {"key": "AAPL|STOCKS", "lastSale": "$1"},
                ]
            }

        monkeypatch.setattr(helpers, "resolve_asset_class", _resolve)
        monkeypatch.setattr(helpers, "get_nasdaq_data", _data)
        rows = asyncio.run(helpers.get_basic_quotes(["AAPL", "MSFT", " "]))

        assert [r["key"] for r in rows] == ["AAPL|STOCKS", "MSFT|STOCKS"]

    def test_raises_when_empty(self, monkeypatch):
        """No matching record is an error."""

        async def _resolve(symbol):
            return "stocks"

        async def _data(path, **kwargs):
            return {"records": []}

        monkeypatch.setattr(helpers, "resolve_asset_class", _resolve)
        monkeypatch.setattr(helpers, "get_nasdaq_data", _data)

        with pytest.raises(EmptyDataError, match="No quotes"):
            asyncio.run(helpers.get_basic_quotes(["AAPL"]))


class TestRequestPaths:
    """Cover the live and cached request paths."""

    def test_live_request_calls_amake_request(self, monkeypatch):
        """The live path delegates to the core request helper."""
        seen: list[tuple] = []

        async def _request(url, **kwargs):
            seen.append((url, kwargs["headers"]["Accept"]))

            return {"ok": True}

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", _request
        )

        assert asyncio.run(helpers._live_request("https://x")) == {"ok": True}
        assert seen[0][1].startswith("application/json")

    def test_cached_request_closes_its_session(self, monkeypatch):
        """The session is closed as soon as the response is read."""
        closed: list[str] = []
        released: list[str] = []

        class _Response:
            async def json(self, content_type=None):
                """Return the decoded body."""
                return {"ok": True}

            def release(self):
                """Record the release."""
                released.append("released")

        class _Session:
            def __init__(self, cache=None):
                pass

            async def __aenter__(self):
                """Enter the session context."""
                return self

            async def __aexit__(self, *args):
                """Record that the session was closed."""
                closed.append("closed")

                return False

            async def get(self, url, **kwargs):
                """Return a canned response."""
                return _Response()

        monkeypatch.setattr("aiohttp_client_cache.session.CachedSession", _Session)

        assert asyncio.run(helpers._cached_request("https://x")) == {"ok": True}
        assert closed == ["closed"]
        assert released == ["released"]

    def test_cached_request_closes_after_a_failure(self, monkeypatch):
        """A response that cannot be read still closes its session."""
        closed: list[str] = []

        class _Response:
            async def json(self, content_type=None):
                """Fail to decode the body."""
                raise ValueError("not json")

        class _Session:
            def __init__(self, cache=None):
                pass

            async def __aenter__(self):
                """Enter the session context."""
                return self

            async def __aexit__(self, *args):
                """Record that the session was closed."""
                closed.append("closed")

                return False

            async def get(self, url, **kwargs):
                """Return a canned response."""
                return _Response()

        monkeypatch.setattr("aiohttp_client_cache.session.CachedSession", _Session)

        with pytest.raises(ValueError, match="not json"):
            asyncio.run(helpers._cached_request("https://x"))

        assert closed == ["closed"]

    def test_cached_request_tolerates_no_release(self, monkeypatch):
        """A response without a release method is still read."""

        class _Response:
            async def json(self, content_type=None):
                """Return the decoded body."""
                return []

        class _Session:
            def __init__(self, cache=None):
                pass

            async def __aenter__(self):
                """Enter the session context."""
                return self

            async def __aexit__(self, *args):
                """Leave the session context."""
                return False

            async def get(self, url, **kwargs):
                """Return a canned response."""
                return _Response()

        monkeypatch.setattr("aiohttp_client_cache.session.CachedSession", _Session)

        assert asyncio.run(helpers._cached_request("https://x")) == []


class TestDirectoryColumns:
    """Cover directory files that omit expected columns."""

    def test_missing_symbol_column(self, monkeypatch):
        """A file without a Symbol column yields an empty index."""
        monkeypatch.setattr(helpers, "get_nasdaq_directory", lambda *a: "A|B\n1|2\n")

        assert helpers._directory_index() == {}

    def test_missing_etf_column_defaults_to_stocks(self, monkeypatch):
        """Without an ETF column every symbol is treated as a stock."""
        monkeypatch.setattr(
            helpers,
            "get_nasdaq_directory",
            lambda *a: "Symbol|Security Name\nAAPL|Apple Inc.\n",
        )

        assert helpers._directory_index() == {"AAPL": "stocks"}
