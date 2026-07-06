"""Tests for the StatsCan economic indicators fetcher (Fase 4).

The fetcher reads from the shipped metadata cache (no network in the
happy path). Tests cover:

- ``_parse_value`` — extracts numeric values from human-readable strings
- ``_parse_refper_to_date`` — parses StatsCan reference periods
- ``StatsCanEconomicIndicatorsFetcher.transform_query`` — defaults & validation
- ``StatsCanEconomicIndicatorsFetcher.extract_data`` — cache lookup + filtering
- ``StatsCanEconomicIndicatorsFetcher.transform_data`` — mapping to standard model
- Empty-cache handling — clear ``OpenBBError`` when cache is empty
- End-to-end — full fetcher round-trip with the seeded cache
"""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_ca.statscan.economic_indicators import (
    StatsCanEconomicIndicatorsData,
    StatsCanEconomicIndicatorsFetcher,
    StatsCanEconomicIndicatorsQueryParams,
    _parse_refper_to_date,
    _parse_value,
)


# ---------------------------------------------------------------------------
# _parse_value
# ---------------------------------------------------------------------------
class TestParseValue:
    """``_parse_value`` extracts the first numeric value from a string."""

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("$47.6 billion", 47.6),
            ("18,161,000", 18161000.0),
            ("-3.9%", -3.9),
            ("83,751.6 million", 83751.6),
            ("0.2%", 0.2),
            ("4.7%", 4.7),
            ("1,234,567.89", 1234567.89),
            ("-$1.5 billion", -1.5),
        ],
    )
    def test_parses_numeric_strings(self, raw, expected):
        """Common StatsCan/BoC value formats parse correctly."""
        assert _parse_value(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            "   ",
            "..",  # StatsCan missing marker
            "...",
            "NaN",
            "N/A",
            "n/a",
            "NA",
            None,
        ],
    )
    def test_returns_none_for_missing_or_invalid(self, raw):
        """Missing/invalid values return ``None``."""
        assert _parse_value(raw) is None

    def test_returns_none_for_no_numeric_content(self):
        """A string with no numeric content returns ``None``."""
        assert _parse_value("no numbers here") is None


# ---------------------------------------------------------------------------
# _parse_refper_to_date
# ---------------------------------------------------------------------------
class TestParseRefperToDate:
    """``_parse_refper_to_date`` parses StatsCan reference periods."""

    @pytest.mark.parametrize(
        "refper,expected",
        [
            ("September 2016", date(2016, 9, 1)),
            ("October 2016", date(2016, 10, 1)),
            ("January 2024", date(2024, 1, 1)),
            ("December 2023", date(2023, 12, 1)),
            ("2016", date(2016, 1, 1)),  # annual
            ("2024", date(2024, 1, 1)),
        ],
    )
    def test_parses_valid_refpers(self, refper, expected):
        """Valid reference periods parse to the first day of the period."""
        assert _parse_refper_to_date(refper) == expected

    @pytest.mark.parametrize(
        "refper",
        [
            "",
            "   ",
            None,
            "not a date",
            "Sept 2016",  # abbreviation not supported
            "13/2016",  # not a recognized format
        ],
    )
    def test_returns_none_for_invalid(self, refper):
        """Invalid reference periods return ``None``."""
        assert _parse_refper_to_date(refper) is None

    def test_case_insensitive_month_name(self):
        """Month name matching is case-insensitive."""
        assert _parse_refper_to_date("SEPTEMBER 2016") == date(2016, 9, 1)
        assert _parse_refper_to_date("september 2016") == date(2016, 9, 1)


# ---------------------------------------------------------------------------
# transform_query
# ---------------------------------------------------------------------------
class TestTransformQuery:
    """``transform_query`` applies defaults and normalizes inputs."""

    def test_defaults_symbol_to_all(self):
        """When no symbol is provided, defaults to ``'all'``."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query({})
        assert q.symbol == "all"

    def test_preserves_explicit_symbol(self):
        """An explicit symbol is preserved."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query({"symbol": "2280069"})
        assert q.symbol == "2280069"

    def test_normalizes_country_canada_to_zero(self):
        """The country name 'canada' is normalized to geo_code '0'."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query({"country": "canada"})
        assert q.country == "0"

    def test_normalizes_country_aliases(self):
        """Common country aliases (CA, CAN) are normalized to '0'."""
        for alias in ("CA", "can", "Canada"):
            q = StatsCanEconomicIndicatorsFetcher.transform_query({"country": alias})
            assert q.country == "0"

    def test_preserves_numeric_geo_code(self):
        """A numeric geo_code is preserved as-is."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query({"country": "1"})
        assert q.country == "1"

    def test_handles_comma_separated_symbols(self):
        """Comma-separated symbols are preserved for later splitting."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query(
            {"symbol": "2280069,Employment"}
        )
        assert "2280069" in q.symbol
        assert "Employment" in q.symbol


# ---------------------------------------------------------------------------
# extract_data
# ---------------------------------------------------------------------------
class TestExtractData:
    """``extract_data`` reads from the cache and filters by query params."""

    def test_returns_all_indicators_for_all_symbol(self, seeded_meta):
        """The 'all' symbol returns every indicator in the cache."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="all")
        result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        assert len(result) == 2  # seeded cache has 2 indicators
        titles = [ind["title_en"] for ind in result]
        assert "Imports" in titles
        assert "Employment" in titles

    def test_filters_by_vector_id(self, seeded_meta):
        """A numeric vector ID returns only the matching indicator."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069")
        result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        assert len(result) == 1
        assert result[0]["source"] == "2280069"
        assert result[0]["title_en"] == "Imports"

    def test_filters_by_title_substring(self, seeded_meta):
        """A title substring returns matching indicators (case-insensitive)."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="employ")
        result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        assert len(result) == 1
        assert result[0]["title_en"] == "Employment"

    def test_filters_by_multiple_symbols(self, seeded_meta):
        """Comma-separated symbols match indicators by either vector ID or title."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069,Employment")
        result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        # Both should match (2280069 = Imports, Employment = Employment).
        assert len(result) == 2

    def test_deduplicates_by_vector_id(self, seeded_meta):
        """When two search terms match the same indicator, it appears only once."""
        # Both "2280069" (vector ID) and "Imports" (title) match the same indicator.
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069,Imports")
        result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        assert len(result) == 1
        assert result[0]["source"] == "2280069"

    def test_raises_empty_data_for_no_match(self, seeded_meta):
        """A symbol that matches nothing raises ``EmptyDataError``."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="zzz_nonexistent_zzz")
        with pytest.raises(EmptyDataError, match="No StatsCan indicators matched"):
            StatsCanEconomicIndicatorsFetcher.extract_data(q, None)

    def test_raises_empty_data_for_empty_cache(self, empty_meta):
        """An empty cache raises ``EmptyDataError``."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="all")
        with pytest.raises(EmptyDataError, match="contains no indicators"):
            StatsCanEconomicIndicatorsFetcher.extract_data(q, None)


# ---------------------------------------------------------------------------
# transform_data
# ---------------------------------------------------------------------------
class TestTransformData:
    """``transform_data`` maps raw indicator dicts to the standard model."""

    def test_maps_basic_fields(self, seeded_meta):
        """Basic fields (symbol, country, value) are mapped correctly."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069")
        raw = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
        assert len(result) == 1
        row = result[0]
        assert row.symbol == "2280069"
        assert row.symbol_root == "Imports"
        assert row.country == "Canada"

    def test_parses_value_from_value_en(self, seeded_meta):
        """The numeric value is parsed from the ``value_en`` string."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069")
        raw = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
        # value_en was "$47.6 billion" → 47.6
        assert result[0].value == 47.6
        # The raw string is preserved.
        assert result[0].value_raw == "$47.6 billion"

    def test_parses_date_from_refper(self, seeded_meta):
        """The date is parsed from the ``refper_en`` string."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069")
        raw = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
        # refper_en was "September 2016" → date(2016, 9, 1)
        assert result[0].date == date(2016, 9, 1)

    def test_preserves_growth_rate_fields(self, seeded_meta):
        """Growth rate, direction, and details are preserved."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069")
        raw = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
        row = result[0]
        assert row.growth_rate == "4.7%"
        assert row.growth_direction == "1"
        assert row.growth_details == "(monthly change)"

    def test_preserves_release_date(self, seeded_meta):
        """The release date is preserved as a string."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="2280069")
        raw = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
        assert result[0].release_date == "2016-11-04"

    def test_sorts_by_date_descending(self, seeded_meta):
        """Results are sorted by date descending (most recent first)."""
        q = StatsCanEconomicIndicatorsQueryParams(symbol="all")
        raw = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
        # Seeded indicators: Imports (Sep 2016), Employment (Oct 2016).
        # Oct should come first.
        assert result[0].date == date(2016, 10, 1)
        assert result[1].date == date(2016, 9, 1)


# ---------------------------------------------------------------------------
# End-to-end: full fetcher round-trip via the .test() helper
# ---------------------------------------------------------------------------
class TestEndToEnd:
    """Full fetcher round-trip mirroring the OECD test pattern."""

    def test_full_round_trip_all_symbol(self, seeded_meta):
        """The fetcher's ``test()`` helper runs end-to-end without error."""
        fetcher = StatsCanEconomicIndicatorsFetcher()
        # The OECD pattern uses fetcher.test(params, credentials) which
        # runs transform_query → extract_data → transform_data.
        result = fetcher.test({"symbol": "all"}, {})
        # ``test`` returns None on success (per the OECD pattern).
        assert result is None

    def test_full_round_trip_with_vector_id(self, seeded_meta):
        """End-to-end with a specific vector ID."""
        fetcher = StatsCanEconomicIndicatorsFetcher()
        result = fetcher.test({"symbol": "2280069"}, {})
        assert result is None

    def test_full_round_trip_with_default_symbol(self, seeded_meta):
        """End-to-end with no symbol (defaults to 'all')."""
        fetcher = StatsCanEconomicIndicatorsFetcher()
        result = fetcher.test({}, {})
        assert result is None


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
class TestDataModel:
    """The ``StatsCanEconomicIndicatorsData`` model accepts all extension fields."""

    def test_accepts_extension_fields(self):
        """The Data model accepts value_raw, refper, growth_rate, etc."""
        row = StatsCanEconomicIndicatorsData(
            date=date(2024, 1, 1),
            symbol_root="Test",
            symbol="12345",
            country="Canada",
            value=42.5,
            value_raw="$42.5 billion",
            refper="January 2024",
            growth_rate="1.2%",
            growth_direction="1",
            growth_details="(monthly change)",
            release_date="2024-02-01",
            daily_url=None,
        )
        assert row.value == 42.5
        assert row.value_raw == "$42.5 billion"
        assert row.refper == "January 2024"

    def test_optional_fields_default_to_none(self):
        """All extension fields default to ``None``."""
        row = StatsCanEconomicIndicatorsData()
        assert row.date is None
        assert row.value is None
        assert row.value_raw is None
        assert row.growth_rate is None
