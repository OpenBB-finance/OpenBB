"""Tests for openbb_cboe.utils.helpers."""

import asyncio
from contextlib import asynccontextmanager
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from pandas import DataFrame

from openbb_cboe.utils import helpers


class FakeResponse:
    """Minimal stand-in for an aiohttp client response."""

    def __init__(self, content_type, payload):
        self.headers = {"Content-Type": content_type}
        self._payload = payload

    async def json(self):
        """Return the JSON payload."""
        return self._payload

    async def text(self):
        """Return the text payload."""
        return self._payload

    async def read(self):
        """Return the raw payload."""
        return self._payload


class FakeCachedSession:
    """Minimal stand-in for ``aiohttp_client_cache.session.CachedSession``."""

    def __init__(self, response):
        self._response = response
        self.closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()

        return False

    async def get(self, url, **kwargs):
        """Return the canned response."""
        self.url = url
        return self._response

    async def close(self):
        """Record that the session was closed."""
        self.closed = True


class TestNewYorkClock:
    """Every session-date default is anchored to America/New_York."""

    def test_ny_now_is_eastern(self):
        """The clock is timezone-aware and offset like New York."""
        from datetime import datetime
        from zoneinfo import ZoneInfo

        now = helpers.ny_now()

        assert now.tzinfo is not None
        assert (
            now.utcoffset() == datetime.now(tz=ZoneInfo("America/New_York")).utcoffset()
        )

    def test_ny_today_is_the_session_date(self):
        """The date is the New York session date, not the machine's."""
        assert helpers.ny_today() == helpers.ny_now().date()


class TestResponseCallback:
    """Content-type dispatch in ``response_callback``."""

    def test_json(self):
        """A JSON content type deserializes the body."""
        response = FakeResponse("application/json", {"a": 1})

        assert asyncio.run(helpers.response_callback(response, None)) == {"a": 1}

    def test_text(self):
        """A text content type returns the decoded body."""
        response = FakeResponse("text/csv", "a,b\n1,2")

        assert asyncio.run(helpers.response_callback(response, None)) == "a,b\n1,2"

    def test_bytes(self):
        """Any other content type returns raw bytes."""
        response = FakeResponse("application/octet-stream", b"\x00\x01")

        assert asyncio.run(helpers.response_callback(response, None)) == b"\x00\x01"


class TestGetCboeData:
    """Cache and no-cache request paths."""

    def test_uses_cached_session(self):
        """With use_cache, the request goes through the SQLite-backed session."""
        from unittest.mock import AsyncMock

        session = FakeCachedSession(FakeResponse("application/json", {"ok": True}))
        backend = SimpleNamespace(close=AsyncMock())

        with (
            patch.object(helpers, "amake_request") as mock_request,
            patch("aiohttp_client_cache.session.CachedSession", return_value=session),
            patch.object(helpers, "cache_backend", AsyncMock(return_value=backend)),
        ):
            result = asyncio.run(helpers.get_cboe_data("https://cboe.test/a.json"))

        assert result == {"ok": True}
        assert session.closed is True
        backend.close.assert_awaited_once()
        mock_request.assert_not_called()

    def test_bypasses_cache(self):
        """Without use_cache, the request goes straight through amake_request."""
        with patch.object(
            helpers, "amake_request", new=AsyncMock(return_value={"ok": False})
        ) as mock_request:
            result = asyncio.run(
                helpers.get_cboe_data("https://cboe.test/a.json", use_cache=False)
            )

        assert result == {"ok": False}
        mock_request.assert_awaited_once()


class TestDirectories:
    """Directory parsing helpers."""

    def test_company_directory(self):
        """The company CSV is renamed and indexed by symbol."""
        csv = (
            b"Company Name, Stock Symbol, DPM Name, Post/Station\n"
            b"APPLE INC,AAPL,Market Maker,1\n"
        )

        with patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)):
            directory = asyncio.run(helpers.get_company_directory())

        assert directory.index.tolist() == ["AAPL"]
        assert directory.loc["AAPL", "name"] == "APPLE INC"
        assert directory.loc["AAPL", "dpm_name"] == "Market Maker"

    def test_au_index_directory(self):
        """CXA definitions are mapped onto the global directory schema."""
        payload = {
            "data": [
                {
                    "symbol": "X2C",
                    "short_name": "CXA 200 Price Return Index",
                    "long_name": "Cboe Australia 200 Price Return Index",
                    "launch_date": "20171204",
                    "series": "CXA 200",
                }
            ]
        }

        with patch.object(
            helpers, "get_cboe_data", new=AsyncMock(return_value=payload)
        ):
            directory = asyncio.run(helpers.get_au_index_directory())

        assert directory.loc[0, "index_symbol"] == "X2C"
        assert directory.loc[0, "currency"] == "AUD"
        assert directory.loc[0, "source"] == "au_proprietary_index"

    def test_index_directory_merges_jurisdictions(self):
        """Morningstar rows are dropped, keys pruned, and CXA rows appended."""
        us_eu = [
            {
                "index_symbol": "BUK100P",
                "name": "Cboe UK 100",
                "source": "eu_proprietary_index",
                "mkt_data_delay": 15,
                "featured": True,
                "featured_order": 1,
                "display": True,
            },
            {
                "index_symbol": "MSTAR",
                "name": "Morningstar",
                "source": "morningstar",
                "featured": False,
                "featured_order": 2,
                "display": False,
            },
        ]
        au = DataFrame(
            [
                {
                    "index_symbol": "X2C",
                    "name": "CXA 200",
                    "currency": "AUD",
                    "source": "au_proprietary_index",
                }
            ]
        )

        catalog = DataFrame(
            [
                {
                    "index_symbol": "BUK100P",
                    "agent_classification": "CO",
                    "channel": "CGI",
                }
            ]
        )

        with (
            patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=us_eu)),
            patch.object(
                helpers, "get_au_index_directory", new=AsyncMock(return_value=au)
            ),
            patch.object(
                helpers, "get_global_indices_feed", new=AsyncMock(return_value=catalog)
            ),
        ):
            directory = asyncio.run(helpers.get_index_directory())

        assert directory["index_symbol"].tolist() == ["BUK100P", "X2C"]
        assert "featured" not in directory.columns
        assert "display" not in directory.columns
        assert directory.loc[1, "mkt_data_delay"] is None
        assert directory.loc[0, "channel"] == "CGI"
        assert directory.loc[1, "channel"] is None


class TestListFutures:
    """Futures root listing."""

    def test_drops_sort_order(self):
        """The presentation-only sort_order key is removed."""
        payload = {"data": [{"future_root": "VX", "sort_order": 1}]}

        with patch.object(
            helpers, "get_cboe_data", new=AsyncMock(return_value=payload)
        ):
            futures = asyncio.run(helpers.list_futures())

        assert futures == [{"future_root": "VX"}]


class TestSettlementPrices:
    """URL selection and parsing for settlement prices."""

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            ({}, "https://www.cboe.com/us/futures/market_statistics/settlement/csv"),
            (
                {"options": True},
                "https://www.cboe.com/us/futures/market_statistics/settlement/csv?options=t",
            ),
            (
                {"settlement_date": date(2024, 6, 27)},
                "https://www.cboe.com/us/futures/market_statistics/settlement/csv?dt=2024-06-27",
            ),
            (
                {"settlement_date": date(2024, 6, 27), "options": True},
                "https://www.cboe.com/us/futures/market_statistics/settlement/csv?options=t&dt=2024-06-27",
            ),
            (
                {"archives": True},
                "https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_FinalSettlement_Archive.csv",
            ),
            (
                {"final_settlement": True},
                "https://www.cboe.com/us/futures/market_statistics/final_settlement_prices/csv/",
            ),
        ],
    )
    def test_url_selection(self, kwargs, expected):
        """Each flag combination resolves to its documented endpoint."""
        csv = "Product,Symbol,Expiration Date,Price\nVX,VX/N4,2024-06-27,12.5\n"
        mock = AsyncMock(return_value=csv)

        with patch.object(helpers, "get_cboe_data", new=mock):
            data = asyncio.run(helpers.get_settlement_prices(**kwargs))

        assert mock.await_args.args[0] == expected
        assert data["expiration"].tolist() == ["2024-06-27"]
        assert data.columns.tolist()[:4] == ["product", "symbol", "expiration", "price"]

    def test_empty_response(self):
        """An empty CSV yields an empty frame."""
        with patch.object(
            helpers, "get_cboe_data", new=AsyncMock(return_value="Product,Price\n")
        ):
            data = asyncio.run(helpers.get_settlement_prices())

        assert data.empty

    def test_session_stamp_is_anchored_to_new_york(self):
        """The live settlement session is stamped with the New York date."""
        csv = "Product,Symbol,Expiration Date,Price\nVX,VX/N4,2026-07-01,12.5\n"

        with (
            patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)),
            patch.object(helpers, "ny_today", return_value=date(2026, 7, 1)),
        ):
            data = asyncio.run(helpers.get_settlement_prices())

        assert data["settlement_date"].tolist() == ["2026-07-01"]


class TestChoices:
    """Widget dropdown choice builders."""

    def test_index_choices(self, index_directory):
        """Every index in the directory becomes a label/value pair."""
        with patch.object(
            helpers, "get_index_directory", new=AsyncMock(return_value=index_directory)
        ):
            choices = asyncio.run(helpers.get_index_choices())

        assert choices == [
            {"label": "BUK100P - Cboe UK 100", "value": "BUK100P"},
            {"label": "AAVE10RP - Cboe Apple 10 Index", "value": "AAVE10RP"},
            {"label": "X2C - CXA 200 Price Return Index", "value": "X2C"},
        ]

    def test_constituent_choices_intersect_supported_symbols(self, index_directory):
        """Only the European and CXA symbols the model accepts are offered."""
        with patch.object(
            helpers, "get_index_directory", new=AsyncMock(return_value=index_directory)
        ):
            choices = asyncio.run(helpers.get_eu_index_choices())

        assert choices == [
            {"label": "BUK100P - Cboe UK 100", "value": "BUK100P"},
            {"label": "X2C - CXA 200 Price Return Index", "value": "X2C"},
        ]

    def test_equity_choices_skip_missing_symbols(self, company_directory):
        """Rows with a non-string symbol are dropped."""
        directory = company_directory.copy()
        directory.loc[float("nan"), "name"] = "BROKEN ROW"

        with patch.object(
            helpers, "get_company_directory", new=AsyncMock(return_value=directory)
        ):
            choices = asyncio.run(helpers.get_equity_choices())

        assert [c["value"] for c in choices] == ["AAPL", "SPY"]
        assert choices[0]["label"] == "AAPL - APPLE INC"


class TestAuConstituents:
    """CXA daily constituent files."""

    def test_parses_constituent_block(self):
        """The constituent block is located and the footer rows dropped."""
        csv = (
            "Net Change,Close,Index Symbol\n"
            "-0.008,1690.87,X2C\n"
            ",,\n"
            "Constituent Name,Closing Price,SEDOL Code,ISIN Code,Symbol,Weight,GICS\n"
            "BHP Group Ltd,42.5,5974437,AU000000BHP4,BHP,0.11176,15104020\n"
            "Dividends,,,,,,\n"
        )

        with patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)):
            rows = asyncio.run(helpers.get_au_index_constituents("X2C"))

        assert len(rows) == 1
        assert rows[0]["Symbol"] == "BHP"
        assert rows[0]["Weight"] == "0.11176"

    def test_decodes_bytes_and_selects_session(self):
        """A bytes body is decoded and 'sod' reads the PREDICT file."""
        csv = (
            b"Close\n1690.87\n,,\nConstituent Name,Symbol,Weight\nBHP Group Ltd,BHP,1\n"
        )
        mock = AsyncMock(return_value=csv)

        with patch.object(helpers, "get_cboe_data", new=mock):
            rows = asyncio.run(helpers.get_au_index_constituents("X2C", session="sod"))

        assert rows[0]["Symbol"] == "BHP"
        assert mock.await_args.args[0].endswith("PREDICT_X2C.csv")

    def test_missing_block_raises(self):
        """A file with no constituent header raises."""
        from openbb_core.provider.utils.errors import EmptyDataError

        with (
            patch.object(
                helpers, "get_cboe_data", new=AsyncMock(return_value="Close\n1690.87\n")
            ),
            pytest.raises(EmptyDataError, match="No constituent data"),
        ):
            asyncio.run(helpers.get_au_index_constituents("X2C"))


class TestIndexHistoryFiles:
    """The published per-symbol daily history files."""

    def test_ohlc_series(self):
        """A volatility index file is parsed as OHLC."""
        csv = "DATE,OPEN,HIGH,LOW,CLOSE\n01/02/1990,17.24,17.24,17.24,17.24\n"

        with patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)):
            rows = asyncio.run(helpers.get_index_history("^VIX"))

        assert rows == [
            {
                "date": "01/02/1990",
                "open": "17.24",
                "high": "17.24",
                "low": "17.24",
                "close": "17.24",
            }
        ]

    def test_close_only_series_is_renamed(self):
        """A symbol-named price column is renamed to 'close'."""
        csv = b"DATE,SPX\n01/02/1975,70.23\n"

        with patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)):
            rows = asyncio.run(helpers.get_index_history("SPX"))

        assert rows == [{"date": "01/02/1975", "close": "70.23"}]

    def test_skips_blank_rows(self):
        """Trailing blank rows are dropped."""
        csv = "DATE,SPX\n01/02/1975,70.23\n,\n"

        with patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)):
            rows = asyncio.run(helpers.get_index_history("SPX"))

        assert len(rows) == 1

    def test_unpublished_symbol_raises(self):
        """A non-CSV body raises."""
        from openbb_core.provider.utils.errors import EmptyDataError

        with (
            patch.object(
                helpers, "get_cboe_data", new=AsyncMock(return_value="<html>404</html>")
            ),
            pytest.raises(EmptyDataError, match="No published history"),
        ):
            asyncio.run(helpers.get_index_history("NOPE"))

    def test_header_only_raises(self):
        """A file with a header and no rows raises."""
        from openbb_core.provider.utils.errors import EmptyDataError

        with (
            patch.object(
                helpers, "get_cboe_data", new=AsyncMock(return_value="DATE,SPX\n")
            ),
            pytest.raises(EmptyDataError, match="No published history"),
        ):
            asyncio.run(helpers.get_index_history("SPX"))


class TestGlobalIndicesFeed:
    """The Global Indices definition feed catalog."""

    def test_parses_channels(self):
        """Symbol, classification, and channel are retained."""
        csv = (
            "Symbol,Description,Agent Classification,Channel,Time and Date of Capture\n"
            ".MSDXUTPU,Morningstar Developed,MS,MSTAR,2026-07-24 15:38:06 CDT\n"
            "BXM,Cboe S&P 500 BuyWrite,CO,CGI,2026-07-24 15:38:06 CDT\n"
        )

        with patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)):
            catalog = asyncio.run(helpers.get_global_indices_feed())

        assert catalog.columns.tolist() == [
            "index_symbol",
            "agent_classification",
            "channel",
        ]
        assert catalog["channel"].tolist() == ["MSTAR", "CGI"]

    def test_decodes_bytes(self):
        """A bytes body is decoded before parsing."""
        csv = (
            b"Symbol,Description,Agent Classification,Channel\n"
            b"BXM,Cboe S&P 500 BuyWrite,CO,CGI\n"
        )

        with patch.object(helpers, "get_cboe_data", new=AsyncMock(return_value=csv)):
            catalog = asyncio.run(helpers.get_global_indices_feed())

        assert catalog["index_symbol"].tolist() == ["BXM"]


class TestIndexDocuments:
    """The bundled index documents catalog."""

    def test_full_catalog(self):
        """With no symbol the whole catalog is returned."""
        catalog = asyncio.run(helpers.get_index_documents())

        assert catalog
        assert {"category", "title", "url"} <= set(catalog[0])
        assert any(d["category"] == "Methodology" for d in catalog)

    def test_symbol_scopes_constituents(self):
        """Symbol-scoped documents include that symbol's constituents file."""
        with patch.object(
            helpers, "amake_request", new=AsyncMock(side_effect=OSError("404"))
        ):
            docs = asyncio.run(helpers.get_index_documents("SPBFA"))

        titles = [d["title"] for d in docs]

        assert "SPBFA Constituents" in titles
        assert "BXMU Constituents" not in titles

    def test_factsheet_prepended_when_published(self):
        """A published factsheet is prepended to the symbol's documents."""
        with patch.object(helpers, "amake_request", new=AsyncMock(return_value=200)):
            docs = asyncio.run(helpers.get_index_documents("^BXM"))

        assert docs[0]["category"] == "Factsheet"
        assert docs[0]["url"].endswith("CboeGlobalIndices_BXM-Index.pdf")

    def test_factsheet_omitted_when_absent(self):
        """No factsheet is added when Cboe does not publish one."""
        with patch.object(
            helpers, "amake_request", new=AsyncMock(side_effect=OSError("403"))
        ):
            docs = asyncio.run(helpers.get_index_documents("VIX"))

        assert not [d for d in docs if d["title"].endswith("Index Factsheet")]

    def test_status_callback(self):
        """The probe callback passes 200 through and raises otherwise."""
        ok = type("R", (), {"status": 200, "url": "u"})()
        bad = type("R", (), {"status": 403, "url": "u"})()

        assert asyncio.run(helpers._status_callback(ok, None)) == 200

        with pytest.raises(OSError, match="403"):
            asyncio.run(helpers._status_callback(bad, None))


class TestIndexDocumentViewer:
    """Cover the document choices and the PDF download behind the viewer."""

    CATALOG = [
        {
            "category": "Governance",
            "title": "Cboe Index Policies & Practices",
            "url": "https://cdn.cboe.com/a.pdf",
        },
        {"category": "Methodology", "title": "No Link", "url": ""},
    ]

    def test_choices_label_each_document(self):
        """Each catalogued document becomes a labelled choice."""
        with patch.object(
            helpers, "get_index_documents", AsyncMock(return_value=self.CATALOG)
        ):
            choices = asyncio.run(helpers.get_document_choices("BXM"))

        assert choices == [
            {
                "label": "Governance - Cboe Index Policies & Practices",
                "value": "https://cdn.cboe.com/a.pdf",
                "extraInfo": {"description": "Cboe Index Policies & Practices"},
            }
        ]

    def test_choices_pass_the_symbol_through(self):
        """The symbol scopes the catalog the choices are built from."""
        catalog = AsyncMock(return_value=[])

        with patch.object(helpers, "get_index_documents", catalog):
            asyncio.run(helpers.get_document_choices("BXM"))

        catalog.assert_awaited_once_with("BXM")

    def test_document_urls_are_validated(self):
        """Only https URLs on a Cboe document host pass."""
        assert helpers.is_cboe_document_url("https://cdn.cboe.com/a.pdf") is True
        assert helpers.is_cboe_document_url("http://cdn.cboe.com/a.pdf") is False
        assert helpers.is_cboe_document_url("https://evil.example/a.pdf") is False
        assert (
            helpers.is_cboe_document_url("https://cdn.cboe.com.evil.example/a.pdf")
            is False
        )
        assert (
            helpers.is_cboe_document_url("https://evil.example/cdn.cboe.com") is False
        )
        assert helpers.is_cboe_document_url(42) is False

    def test_download_refuses_foreign_hosts(self):
        """A URL off the allowlist is refused before any request is made."""
        with pytest.raises(OSError, match="Refusing"):
            asyncio.run(helpers.download_index_document("https://evil.example/a.pdf"))

    def test_download_is_base64(self):
        """The PDF body is read through the callback and base64-encoded."""

        class Response:
            """A stand-in carrying a PDF body."""

            async def read(self):
                """Return the raw body."""
                return b"%PDF-1.4 body"

        async def request(url, **kwargs):
            """Invoke the response callback the helper supplies."""
            return await kwargs["response_callback"](Response(), None)

        with patch(
            "openbb_core.provider.utils.helpers.amake_request", side_effect=request
        ):
            encoded = asyncio.run(
                helpers.download_index_document("https://cdn.cboe.com/a.pdf")
            )

        assert encoded == "JVBERi0xLjQgYm9keQ=="

    def test_open_returns_the_viewer_payload(self):
        """A successful download carries the data format and filename."""
        with patch.object(
            helpers, "download_index_document", AsyncMock(return_value="QUJD")
        ):
            payload = asyncio.run(
                helpers.open_index_document("https://cdn.cboe.com/BXM.pdf")
            )

        assert payload == {
            "content": "QUJD",
            "data_format": {"data_type": "pdf", "filename": "BXM.pdf"},
        }

    def test_open_falls_back_to_a_generic_filename(self):
        """A URL ending in a separator still names the document."""
        with patch.object(
            helpers, "download_index_document", AsyncMock(return_value="QUJD")
        ):
            payload = asyncio.run(helpers.open_index_document("https://cdn.cboe.com/"))

        assert payload["data_format"]["filename"] == "document.pdf"

    def test_open_reports_a_failure(self):
        """A failed download is surfaced as an error payload."""
        with patch.object(
            helpers,
            "download_index_document",
            AsyncMock(side_effect=OSError("404")),
        ):
            payload = asyncio.run(
                helpers.open_index_document("https://cdn.cboe.com/a.pdf")
            )

        assert payload["error_type"] == "download_error"
        assert "404" in payload["content"]


async def _empty():
    """Yield no keys at all."""
    for key in ():
        yield key


async def _keys(count):
    """Yield as many keys as the cache is said to hold."""
    for index in range(count):
        yield f"key{index}"


@asynccontextmanager
async def _connection():
    """Stand in for the aiosqlite connection a vacuum runs on."""

    class Connection:
        async def execute(self, statement):
            return None

    yield Connection()


class TestResponseCache:
    """The on-disk cache is bounded by age and by size."""

    def test_each_endpoint_keeps_for_as_long_as_it_stays_good(self):
        """A quote feed must not be held for as long as a directory."""
        from aiohttp_client_cache.cache_control import get_url_expiration

        expiry = {
            "https://ww2.cboe.com/json/bats_eu/book/BUK100P": 60,
            "https://ww2.cboe.com/education/tools/trade-optimizer"
            "/trade-optimizer-data/?symbol=SPY": 600,
            "https://cdn.cboe.com/api/global/us_indices/definitions"
            "/GlobalIndices.csv": 900,
            "https://cdn.cboe.com/api/global/us_indices/daily_prices"
            "/VIX_History.csv": 3600 * 6,
            "https://www.cboe.com/us/options/symboldir"
            "/equity_index_options/?download=csv": 3600 * 24,
        }

        for url, seconds in expiry.items():
            assert get_url_expiration(url, helpers.CACHE_TTL) == seconds, url

    def test_one_cache_is_shared_by_every_request(self):
        """A backend per request opens the file again for each one."""
        from unittest.mock import patch

        async def twice():
            return await helpers.cache_backend(), await helpers.cache_backend()

        with (
            patch.object(helpers, "_cache", None),
            patch.object(helpers, "_cache_loop", None),
            patch.object(helpers, "_cache_users", 0),
            patch.object(helpers, "_swept", True),
        ):
            first, second = asyncio.run(twice())

        assert first is second

    def test_a_new_event_loop_gets_a_fresh_backend(self):
        """Locks bound to a finished loop must not leak into the next one."""
        from unittest.mock import patch

        with (
            patch.object(helpers, "_cache", None),
            patch.object(helpers, "_cache_loop", None),
            patch.object(helpers, "_cache_users", 0),
            patch.object(helpers, "_swept", True),
        ):
            first = asyncio.run(helpers.cache_backend())
            second = asyncio.run(helpers.cache_backend())

        assert first is not second

    def test_the_backend_outlives_any_one_session(self):
        """A session closing on exit must not take the shared connection with it."""
        from unittest.mock import patch

        with (
            patch.object(helpers, "_cache", None),
            patch.object(helpers, "_cache_loop", None),
            patch.object(helpers, "_cache_users", 0),
            patch.object(helpers, "_swept", True),
        ):
            backend = asyncio.run(helpers.cache_backend())

        assert backend.autoclose is False

    def test_a_failing_sweep_still_returns_the_backend(self):
        """A sweep failure is logged, never raised into the request."""
        from unittest.mock import patch

        with (
            patch.object(helpers, "_cache", None),
            patch.object(helpers, "_cache_loop", None),
            patch.object(helpers, "_cache_users", 0),
            patch.object(helpers, "_swept", False),
            patch.object(
                helpers, "_sweep", new=AsyncMock(side_effect=Exception("boom"))
            ),
        ):
            backend = asyncio.run(helpers.cache_backend())

        assert backend is not None

    def test_the_shared_cache_closes_only_after_the_last_request(self):
        """A request finishing must not close the connection under another."""
        from asyncio import Event, create_task, sleep

        fake_cache = SimpleNamespace(close=AsyncMock())
        gate = Event()
        overlap_closes: list = []

        class GatedSession(FakeCachedSession):
            async def get(self, url, **kwargs):
                if "slow" in url:
                    await gate.wait()

                return await super().get(url, **kwargs)

        async def scenario():
            slow = create_task(helpers.get_cboe_data("https://cboe.test/slow.json"))

            while helpers._cache_users == 0:
                await sleep(0)

            await helpers.get_cboe_data("https://cboe.test/fast.json")
            overlap_closes.append(fake_cache.close.await_count)
            gate.set()
            await slow

        with (
            patch(
                "aiohttp_client_cache.session.CachedSession",
                side_effect=lambda **kwargs: GatedSession(
                    FakeResponse("application/json", {"ok": True})
                ),
            ),
            patch.object(helpers, "cache_backend", AsyncMock(return_value=fake_cache)),
            patch.object(helpers, "_cache_users", 0),
        ):
            asyncio.run(scenario())

        assert overlap_closes == [0]
        fake_cache.close.assert_awaited_once()

    def test_an_expired_response_is_deleted_not_just_ignored(self, tmp_path):
        """An expiry alone leaves the row behind and the file grows forever."""
        from unittest.mock import AsyncMock, patch

        backend = SimpleNamespace(
            delete_expired_responses=AsyncMock(),
            responses=SimpleNamespace(
                size=AsyncMock(return_value=0),
                keys=_empty,
                bulk_delete=AsyncMock(),
                get_connection=lambda commit=False: _connection(),
            ),
        )

        with patch.object(helpers, "cache_path", lambda: str(tmp_path / "absent")):
            asyncio.run(helpers._sweep(backend))

        backend.delete_expired_responses.assert_awaited_once()

    def test_a_file_over_the_limit_drops_its_oldest(self, tmp_path):
        """What the sweep leaves over the limit is trimmed by the overshoot."""
        from unittest.mock import AsyncMock, patch

        stored = tmp_path / "probe.sqlite"
        stored.write_bytes(b"x" * 1000)
        dropped: list = []

        async def bulk_delete(keys):
            dropped.append(len(keys))
            stored.write_bytes(b"x" * 100)

        backend = SimpleNamespace(
            delete_expired_responses=AsyncMock(),
            responses=SimpleNamespace(
                size=AsyncMock(return_value=10),
                keys=lambda: _keys(10),
                bulk_delete=bulk_delete,
                get_connection=lambda commit=False: _connection(),
            ),
        )

        with (
            patch.object(helpers, "cache_path", lambda: str(tmp_path / "probe")),
            patch.object(helpers, "CACHE_MAX_BYTES", 500),
        ):
            asyncio.run(helpers._sweep(backend))

        assert dropped == [5]
        assert stored.stat().st_size <= 500

    def test_a_sweep_with_nothing_left_to_drop_stops(self, tmp_path):
        """An oversized file whose entries are already gone is not re-trimmed."""
        from unittest.mock import AsyncMock, patch

        stored = tmp_path / "probe.sqlite"
        stored.write_bytes(b"x" * 1000)
        backend = SimpleNamespace(
            delete_expired_responses=AsyncMock(),
            responses=SimpleNamespace(
                size=AsyncMock(return_value=0),
                keys=_empty,
                bulk_delete=AsyncMock(),
                get_connection=lambda commit=False: _connection(),
            ),
        )

        with (
            patch.object(helpers, "cache_path", lambda: str(tmp_path / "probe")),
            patch.object(helpers, "CACHE_MAX_BYTES", 500),
        ):
            asyncio.run(helpers._sweep(backend))

        backend.responses.bulk_delete.assert_not_awaited()

    def test_a_file_under_the_limit_is_left_alone(self, tmp_path):
        from unittest.mock import AsyncMock, patch

        stored = tmp_path / "probe.sqlite"
        stored.write_bytes(b"x" * 100)
        backend = SimpleNamespace(
            delete_expired_responses=AsyncMock(),
            responses=SimpleNamespace(
                size=AsyncMock(return_value=10),
                keys=lambda: _keys(10),
                bulk_delete=AsyncMock(),
                get_connection=lambda commit=False: _connection(),
            ),
        )

        with (
            patch.object(helpers, "cache_path", lambda: str(tmp_path / "probe")),
            patch.object(helpers, "CACHE_MAX_BYTES", 500),
        ):
            asyncio.run(helpers._sweep(backend))

        backend.responses.bulk_delete.assert_not_awaited()


class TestCacheBackendReuse:
    """A closed backend must never be handed back out."""

    def test_a_second_request_does_not_reuse_a_closed_backend(self):
        """Closing on the last request must not poison every request after it.

        ``SQLiteBackend.close()`` clears the connection object it was built with
        and never rebuilds it, so holding the reference made the first completed
        request break all later ones with ``'NoneType' object has no attribute
        '_connection'``.
        """
        from unittest.mock import patch

        with (
            patch.object(helpers, "_cache", None),
            patch.object(helpers, "_cache_loop", None),
            patch.object(helpers, "_cache_users", 0),
            patch.object(helpers, "_swept", True),
        ):

            async def _two_requests():
                first = await helpers.cache_backend()
                await helpers.close_cache_backend(first)
                second = await helpers.cache_backend()
                return first, second

            first, second = asyncio.run(_two_requests())

        assert second is not first

    def test_closing_clears_the_shared_reference(self):
        """After a close, nothing is left pointing at the dead backend."""
        from unittest.mock import patch

        with (
            patch.object(helpers, "_cache", None),
            patch.object(helpers, "_cache_loop", None),
            patch.object(helpers, "_cache_users", 0),
            patch.object(helpers, "_swept", True),
        ):
            backend = asyncio.run(helpers.cache_backend())
            assert helpers._cache is backend

            asyncio.run(helpers.close_cache_backend(backend))

            assert helpers._cache is None
            assert helpers._cache_loop is None

    def test_closing_a_stale_backend_leaves_the_current_one(self):
        """A late close from an old request must not drop a newer shared backend."""
        from unittest.mock import AsyncMock, patch

        stale = SimpleNamespace(close=AsyncMock())
        current = SimpleNamespace(close=AsyncMock())

        with (
            patch.object(helpers, "_cache", current),
            patch.object(helpers, "_cache_loop", "loop"),
        ):
            asyncio.run(helpers.close_cache_backend(stale))

            assert helpers._cache is current
            assert helpers._cache_loop == "loop"

        stale.close.assert_awaited_once()
        current.close.assert_not_called()

    def test_a_failing_close_is_swallowed(self):
        """A close error must not surface as the request's failure."""
        from unittest.mock import AsyncMock, patch

        backend = SimpleNamespace(close=AsyncMock(side_effect=Exception("locked")))

        with (
            patch.object(helpers, "_cache", backend),
            patch.object(helpers, "_cache_loop", "loop"),
        ):
            asyncio.run(helpers.close_cache_backend(backend))

        assert helpers._cache is None
