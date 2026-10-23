"""Tests for the financials, Nordic, and query-param utilities."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_nasdaq.utils import financials, nordic


class TestFinancials:
    """Cover the statement fetch and pivot."""

    @staticmethod
    def _payload():
        """Return a two-period income statement payload."""
        return {
            "incomeStatementTable": {
                "headers": {
                    "value1": "Period Ending:",
                    "value2": "12/31/2025",
                    "value3": "12/31/2024",
                    "value4": "N/A",
                },
                "rows": [
                    {"value1": "Total Revenue", "value2": "$1,000", "value3": "$900"},
                    {"value1": "Net Income", "value2": "$100", "value3": ""},
                    {"value1": "Unmapped Line", "value2": "$5", "value3": "$5"},
                ],
            },
            "financialRatiosTable": {
                "headers": {"value1": "Period Ending:", "value2": "12/31/2025"},
                "rows": [{"value1": "Profit Margin", "value2": "10.00 %"}],
            },
        }

    def test_get_financials_maps_the_frequency(self, monkeypatch):
        """Annual and quarterly map to the Nasdaq frequency codes."""
        seen: list[str] = []

        async def _data(path, **kwargs):
            seen.append(path)

            return {}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        asyncio.run(financials.get_financials("aapl", "annual"))
        asyncio.run(financials.get_financials("aapl", "quarter"))

        assert "frequency=1" in seen[0]
        assert "frequency=2" in seen[1]
        assert "AAPL" in seen[0]

    def test_pivots_by_period(self):
        """Each column becomes a record, newest first."""
        rows = financials.parse_statement(
            self._payload(),
            "income",
            financials.INCOME_STATEMENT_MAP,
            "aapl",
            "annual",
        )

        assert len(rows) == 2
        assert rows[0]["fiscal_year"] == 2025
        assert rows[0]["symbol"] == "AAPL"
        assert rows[0]["fiscal_period"] == "annual"

    def test_skips_unparseable_periods(self):
        """A column whose header is not a date is dropped."""
        periods = [
            r["period_ending"].isoformat()
            for r in financials.parse_statement(
                self._payload(),
                "income",
                financials.INCOME_STATEMENT_MAP,
                "AAPL",
                "annual",
            )
        ]

        assert periods == ["2025-12-31", "2024-12-31"]

    def test_normalizes_percent_ratios(self):
        """Ratios published as percentages are normalized."""
        rows = financials.parse_statement(
            self._payload(),
            "ratios",
            financials.FINANCIAL_RATIOS_MAP,
            "AAPL",
            "annual",
        )

        assert rows[0]["net_profit_margin"] == pytest.approx(0.1)

    def test_empty_payload(self):
        """A missing table yields no records."""
        assert (
            financials.parse_statement(
                {}, "balance", financials.BALANCE_SHEET_MAP, "AAPL", "annual"
            )
            == []
        )


class TestNordicDirectory:
    """Cover the Nasdaq Nordic instrument directory."""

    @staticmethod
    def _row(symbol, orderbook_id, asset_class="SHARES"):
        """Return one raw screener row."""
        return {
            "symbol": symbol,
            "orderbookId": orderbook_id,
            "assetClass": asset_class,
            "fullName": f"{symbol} AB",
            "isin": f"SE{symbol}",
        }

    def _patch(self, monkeypatch, pages, recorder=None):
        """Serve canned pages keyed by the request path."""

        async def _page(path, query, page):
            if recorder is not None:
                recorder.append((path, query, page))

            return pages(path, query, page)

        monkeypatch.setattr(nordic, "_directory_page", _page)

    def test_indexes_every_listing(self, monkeypatch):
        """Every listing and market contributes to one directory."""
        seen: list[tuple] = []
        self._patch(
            monkeypatch,
            lambda path, query, page: ([self._row(f"{path}-{page}", "TX1")], 1),
            seen,
        )
        directory = asyncio.run(nordic.get_nordic_directory())

        assert {path for path, _, _ in seen} == set(nordic.NORDIC_PATHS.values())
        assert len(directory) == len({path for path, _, _ in seen})

    def test_indexes_use_the_market_filter(self, monkeypatch):
        """The index listing is segmented by market, not category."""
        seen: list[tuple] = []
        self._patch(monkeypatch, lambda path, query, page: ([], 1), seen)
        asyncio.run(nordic.get_nordic_directory())
        index_queries = {q for path, q, _ in seen if path == "indexes"}

        assert index_queries == {
            f"&market={group}" for group in nordic.NORDIC_INDEX_MARKETS
        }

    def test_fetches_remaining_pages(self, monkeypatch):
        """A listing reporting several pages has the remainder fetched."""
        seen: list[tuple] = []

        def _pages(path, query, page):
            if path == "shares":
                return [self._row(f"S{page}", "TX1")], 3

            return [], 1

        self._patch(monkeypatch, _pages, seen)
        directory = asyncio.run(nordic.get_nordic_directory())
        share_pages = sorted(p for path, _, p in seen if path == "shares")

        assert share_pages == [1, 1, 1, 2, 2, 2, 3, 3, 3]
        assert {"S1", "S2", "S3"} <= set(directory)

    def test_first_listing_claims_a_symbol(self, monkeypatch):
        """A symbol listed twice keeps the first listing that claimed it."""
        self._patch(
            monkeypatch, lambda path, query, page: ([self._row("DUP", "TX1")], 1)
        )
        directory = asyncio.run(nordic.get_nordic_directory())

        assert directory["DUP"]["listing"] == nordic.NORDIC_PROBE_ORDER[0]

    def test_skips_rows_without_a_symbol(self, monkeypatch):
        """A row carrying no symbol is not indexed."""
        self._patch(
            monkeypatch, lambda path, query, page: ([{"orderbookId": "TX1"}], 1)
        )

        assert asyncio.run(nordic.get_nordic_directory()) == {}

    def test_survives_a_failing_listing(self, monkeypatch):
        """A listing that errors does not sink the directory."""

        async def _page(path, query, page):
            if path == "shares":
                raise OpenBBError("upstream")

            return [self._row(f"{path}", "TX1")], 1

        monkeypatch.setattr(nordic, "_directory_page", _page)
        directory = asyncio.run(nordic.get_nordic_directory())

        assert "shares" not in {r["listing"] for r in directory.values()}
        assert directory

    def test_survives_a_failing_later_page(self, monkeypatch):
        """A later page that errors does not sink the listing."""
        calls: list[int] = []

        async def _page(path, query, page):
            calls.append(page)

            if page > 1:
                raise OpenBBError("upstream")

            return [self._row(f"{path}-1", "TX1")], 2

        monkeypatch.setattr(nordic, "_directory_page", _page)

        assert asyncio.run(nordic.get_nordic_directory())
        assert 2 in calls

    def test_page_request_shape(self, monkeypatch):
        """A page request carries the size, page, and listing filter."""
        seen: list[str] = []

        async def _data(path, **kwargs):
            seen.append(path)

            return {
                "instrumentListing": {"rows": [{"symbol": "X"}]},
                "pagination": {"totalPages": "2"},
            }

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        rows, pages = asyncio.run(
            nordic._directory_page("shares", "&category=MAIN_MARKET", 1)
        )

        assert rows == [{"symbol": "X"}]
        assert pages == 2
        assert "size=1000" in seen[0]
        assert "page=1" in seen[0]
        assert "category=MAIN_MARKET" in seen[0]

    def test_page_request_without_a_payload(self, monkeypatch):
        """An empty response yields no rows and a single page."""

        async def _data(path, **kwargs):
            return None

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)

        assert asyncio.run(nordic._directory_page("funds", "", 1)) == ([], 1)


class TestNordicSymbolChoices:
    """Cover the Nordic instrument picker."""

    def test_describes_each_instrument(self, monkeypatch):
        """Each choice carries the name, listing, and ISIN."""

        async def _directory():
            return {
                "ATCO A": {
                    "orderbook_id": "TX63",
                    "asset_class": "SHARES",
                    "listing": "shares",
                    "name": "Atlas Copco A",
                    "isin": "SE0017486889",
                },
                "NOISIN": {
                    "orderbook_id": "TX1",
                    "asset_class": "SHARES",
                    "listing": "corporate_bonds",
                    "name": None,
                    "isin": None,
                },
            }

        monkeypatch.setattr(nordic, "get_nordic_directory", _directory)
        choices = asyncio.run(nordic.get_nordic_symbol_choices())

        assert [c["value"] for c in choices] == ["ATCO A", "NOISIN"]
        assert (
            choices[0]["extraInfo"]["description"]
            == "Atlas Copco A - shares (SE0017486889)"
        )
        assert choices[1]["extraInfo"]["description"] == "NOISIN - corporate bonds"


class TestResolveNordicInstrument:
    """Cover the symbol lookup."""

    def test_resolves_from_the_directory(self, monkeypatch):
        """A listed symbol resolves to its orderbook identifier."""

        async def _directory():
            return {"ATCO A": {"orderbook_id": "TX63", "asset_class": "SHARES"}}

        monkeypatch.setattr(nordic, "get_nordic_directory", _directory)
        found = asyncio.run(nordic.resolve_nordic_instrument("atco a"))

        assert found["orderbook_id"] == "TX63"

    def test_unknown_symbol_raises(self, monkeypatch):
        """A symbol in no listing is reported."""

        async def _directory():
            return {}

        monkeypatch.setattr(nordic, "get_nordic_directory", _directory)

        with pytest.raises(OpenBBError, match="was not found"):
            asyncio.run(nordic.resolve_nordic_instrument("NOPE"))


class TestNordicDirectoryPageRetries:
    """Cover the retry the directory applies to refused pages."""

    @staticmethod
    def _patch_sleep(monkeypatch):
        """Make the backoff instant."""
        monkeypatch.setattr(nordic, "DIRECTORY_BACKOFF", 0)

    def test_retries_an_error(self, monkeypatch):
        """A page that errors is retried before it is given up on."""
        self._patch_sleep(monkeypatch)
        attempts: list[int] = []

        async def _data(path, **kwargs):
            attempts.append(1)

            if len(attempts) < 2:
                raise OpenBBError("refused")

            return {
                "instrumentListing": {"rows": [{"symbol": "X"}]},
                "pagination": {"totalPages": "1"},
            }

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        rows, pages = asyncio.run(nordic._directory_page("shares", "", 1))

        assert len(attempts) == 2
        assert rows == [{"symbol": "X"}]

    def test_raises_after_every_attempt(self, monkeypatch):
        """A page that never answers is surfaced."""
        self._patch_sleep(monkeypatch)

        async def _data(path, **kwargs):
            raise OpenBBError("refused")

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)

        with pytest.raises(OpenBBError, match="refused"):
            asyncio.run(nordic._directory_page("shares", "", 1))

    def test_retries_an_empty_later_page(self, monkeypatch):
        """Nasdaq refuses under load by returning an empty page, so it retries."""
        self._patch_sleep(monkeypatch)
        attempts: list[int] = []

        async def _data(path, **kwargs):
            attempts.append(1)
            rows = [] if len(attempts) < 2 else [{"symbol": "X"}]

            return {
                "instrumentListing": {"rows": rows},
                "pagination": {"totalPages": "5"},
            }

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        rows, _ = asyncio.run(nordic._directory_page("shares", "", 3))

        assert len(attempts) == 2
        assert rows == [{"symbol": "X"}]

    def test_accepts_a_genuinely_empty_later_page(self, monkeypatch):
        """A page still empty after every attempt is accepted as empty."""
        self._patch_sleep(monkeypatch)
        attempts: list[int] = []

        async def _data(path, **kwargs):
            attempts.append(1)

            return {
                "instrumentListing": {"rows": []},
                "pagination": {"totalPages": "5"},
            }

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        rows, _ = asyncio.run(nordic._directory_page("shares", "", 3))

        assert rows == []
        assert len(attempts) == nordic.DIRECTORY_ATTEMPTS

    def test_accepts_an_empty_first_page(self, monkeypatch):
        """An empty first page is a genuinely empty listing, not a refusal."""
        self._patch_sleep(monkeypatch)
        attempts: list[int] = []

        async def _data(path, **kwargs):
            attempts.append(1)

            return {"rows": [], "pagination": {"totalPages": "1"}}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)

        assert asyncio.run(nordic._directory_page("etp", "&category=AMF", 1)) == ([], 1)
        assert len(attempts) == 1

    def test_reads_the_flat_envelope(self, monkeypatch):
        """The custom basket listing returns its rows at the top level."""

        async def _data(path, **kwargs):
            return {"rows": [{"symbol": "SBN0196I"}]}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        rows, pages = asyncio.run(
            nordic._directory_page("custom-basket-forwards", "", 1)
        )

        assert rows == [{"symbol": "SBN0196I"}]
        assert pages == 1
