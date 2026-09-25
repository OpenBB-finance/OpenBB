"""Tests for the Nasdaq equity screener model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_nasdaq.models.equity_screener import (
    NasdaqEquityScreenerFetcher,
    NasdaqEquityScreenerQueryParams,
)


class TestScreenerFilters:
    """Cover the filter validators."""

    @pytest.mark.parametrize(
        ("field", "valid", "invalid"),
        [
            ("exchange", "nasdaq", "moon"),
            ("exsubcategory", "ngs", "moon"),
            ("mktcap", "mega", "moon"),
            ("recommendation", "strong_buy", "moon"),
            ("sector", "technology", "moon"),
            ("region", "north_america", "moon"),
        ],
    )
    def test_keeps_valid_and_warns_on_invalid(self, field, valid, invalid):
        """Recognised filters are kept and unknown ones warn."""
        query = NasdaqEquityScreenerQueryParams(**{field: valid})

        assert getattr(query, field) == valid

        with pytest.warns(UserWarning, match="Invalid"):
            query = NasdaqEquityScreenerQueryParams(**{field: invalid})

        assert getattr(query, field) == "all"

    @pytest.mark.parametrize(
        "field",
        ["exchange", "exsubcategory", "mktcap", "recommendation", "sector", "region"],
    )
    def test_all_is_dropped(self, field):
        """The catch-all value collapses to 'all'."""
        assert (
            getattr(NasdaqEquityScreenerQueryParams(**{field: "all"}), field) == "all"
        )

    def test_combines_multiple_filters(self):
        """A comma-separated list keeps every recognised value."""
        query = NasdaqEquityScreenerQueryParams(exchange="nasdaq,nyse")

        assert query.exchange == "nasdaq,nyse"

    def test_country_accepts_a_snake_case_name(self):
        """A snake-case country name is kept."""
        assert (
            NasdaqEquityScreenerQueryParams(country="united_states").country
            == "united_states"
        )

    def test_country_normalizes_an_iso_code(self):
        """An ISO code is normalized to the Nasdaq snake-case name."""
        assert NasdaqEquityScreenerQueryParams(country="US").country == "united_states"

    def test_country_warns_on_an_unknown_value(self):
        """An unrecognised country warns and collapses to 'all'."""
        with pytest.warns(UserWarning, match="Invalid country"):
            query = NasdaqEquityScreenerQueryParams(country="atlantis")

        assert query.country == "all"


class TestScreenerRequest:
    """Cover the screener request construction."""

    @staticmethod
    def _patch(monkeypatch, recorder, payload=None):
        """Point the screener at a canned response."""

        class _Response:
            def json(self):
                """Return the canned payload."""
                return payload or {"data": {"rows": []}}

        def _request(url, **kwargs):
            recorder.append(url)

            return _Response()

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)

    def test_omits_filters_left_at_all(self, monkeypatch):
        """Filters left unset are not sent."""
        seen: list[str] = []
        self._patch(monkeypatch, seen)
        query = NasdaqEquityScreenerFetcher.transform_query({})
        NasdaqEquityScreenerFetcher.extract_data(query, None)

        assert seen[0].endswith("download=true&")

    def test_sends_the_selected_filters(self, monkeypatch):
        """Selected filters are upper-cased and pipe-joined where required."""
        seen: list[str] = []
        self._patch(monkeypatch, seen)
        query = NasdaqEquityScreenerFetcher.transform_query(
            {"exchange": "nasdaq,nyse", "mktcap": "mega", "sector": "technology"}
        )
        NasdaqEquityScreenerFetcher.extract_data(query, None)

        assert "exchange=NASDAQ|NYSE" in seen[0]
        assert "marketcap=mega" in seen[0]
        assert "sector=technology" in seen[0]

    def test_renames_the_nasdaq_sector_aliases(self, monkeypatch):
        """The two sectors Nasdaq names differently are translated."""
        seen: list[str] = []
        self._patch(monkeypatch, seen)
        query = NasdaqEquityScreenerFetcher.transform_query(
            {"sector": "financial_services"}
        )
        NasdaqEquityScreenerFetcher.extract_data(query, None)

        assert "sector=finance" in seen[0]

    def test_wraps_a_request_failure(self, monkeypatch):
        """A failed request is reported as an OpenBBError."""

        def _request(url, **kwargs):
            raise OSError("offline")

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _request)
        query = NasdaqEquityScreenerFetcher.transform_query({})

        with pytest.raises(OpenBBError, match="Failed to get data from Nasdaq"):
            NasdaqEquityScreenerFetcher.extract_data(query, None)


class TestScreenerResults:
    """Cover the screener result transform."""

    @staticmethod
    def _row(symbol="AAPL", pct="3.53%"):
        """Return one screener row."""
        return {
            "symbol": symbol,
            "name": "Apple Inc. Common Stock",
            "lastsale": "$333.02",
            "netchange": "11.36",
            "pctchange": pct,
            "marketCap": "5,000,000",
            "volume": "47,489,726",
            "country": "United States",
            "ipoyear": "1980",
            "industry": "Computer Manufacturing",
            "sector": "Technology",
            "url": "/market-activity/stocks/aapl",
            "deltaIndicator": "up",
        }

    def test_transforms_and_sorts(self):
        """Rows sort by percent change and the noise columns are dropped."""
        query = NasdaqEquityScreenerFetcher.transform_query({})
        rows = NasdaqEquityScreenerFetcher.transform_data(
            query,
            {
                "data": {
                    "rows": [self._row("MSFT", "1.00%"), self._row("AAPL", "3.53%")]
                }
            },
        )

        assert [r.symbol for r in rows] == ["AAPL", "MSFT"]
        assert rows[0].change_percent == pytest.approx(0.0353)
        assert rows[0].last_price == pytest.approx(333.02)
        assert rows[0].market_cap == pytest.approx(5000000)

    def test_reads_the_nested_table(self):
        """A payload nesting rows under a table is read."""
        query = NasdaqEquityScreenerFetcher.transform_query({})
        rows = NasdaqEquityScreenerFetcher.transform_data(
            query, {"data": {"table": {"rows": [self._row()]}}}
        )

        assert rows[0].symbol == "AAPL"

    def test_limit_truncates(self):
        """The limit caps the number of rows returned."""
        query = NasdaqEquityScreenerFetcher.transform_query({"limit": 1})
        rows = NasdaqEquityScreenerFetcher.transform_data(
            query, {"data": {"rows": [self._row("AAPL"), self._row("MSFT")]}}
        )

        assert len(rows) == 1

    def test_normalizes_placeholder_numbers(self):
        """Nasdaq's placeholder values become None."""
        query = NasdaqEquityScreenerFetcher.transform_query({})
        row = self._row()
        row.update(netchange="UNCH", volume="--", ipoyear="NA")
        rows = NasdaqEquityScreenerFetcher.transform_data(
            query, {"data": {"rows": [row]}}
        )

        assert rows[0].change is None
        assert rows[0].volume is None
        assert rows[0].ipo_year is None

    def test_empty_payload_raises(self):
        """An empty response is reported."""
        query = NasdaqEquityScreenerFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="returned empty"):
            NasdaqEquityScreenerFetcher.transform_data(query, {})

    def test_no_rows_raises(self):
        """A response with no matching rows is reported."""
        query = NasdaqEquityScreenerFetcher.transform_query({})

        with pytest.raises(EmptyDataError, match="No results"):
            NasdaqEquityScreenerFetcher.transform_data(query, {"data": {"rows": []}})


class TestScreenerCountryTypes:
    """Cover the country validator's accepted input forms."""

    def test_accepts_a_country_enum(self):
        """A Country member is converted to Nasdaq's snake-case name."""
        from openbb_core.provider.utils.country_utils import Country

        query = NasdaqEquityScreenerQueryParams(country=Country("united_states"))

        assert query.country == "united_states"

    def test_drops_the_catch_all_country(self):
        """The catch-all country collapses to 'all'."""
        assert NasdaqEquityScreenerQueryParams(country="all").country == "all"

    def test_non_string_numbers_pass_through(self):
        """A value that is already numeric is not re-parsed."""
        from openbb_nasdaq.models.equity_screener import NasdaqEquityScreenerData

        row = NasdaqEquityScreenerData.model_validate(
            {"symbol": "AAPL", "name": "Apple", "lastsale": "$1.00", "volume": 1000}
        )

        assert row.volume == 1000
