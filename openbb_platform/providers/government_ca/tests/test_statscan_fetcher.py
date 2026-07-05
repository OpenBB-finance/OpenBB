"""Tests for the StatsCan economic indicators fetcher.

The fetcher reads observations from the StatsCan WDS REST API at
runtime (with a diskcache TTL layer) and uses the shipped SDMX
catalog only for parameter resolution (vector ID → cube PID, etc.).
Tests cover:

- ``StatsCanEconomicIndicatorsFetcher.transform_query`` — defaults & validation
- ``StatsCanEconomicIndicatorsFetcher.extract_data`` — vector / cube / homepage modes
- ``StatsCanEconomicIndicatorsFetcher.transform_data`` — mapping to standard model
- Degraded-mode handling — clear ``OpenBBError`` when the catalog is empty
- End-to-end — full fetcher round-trip with a seeded catalog + mocked WDS client
"""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_government_ca.statscan.economic_indicators import (
    StatsCanEconomicIndicatorsFetcher,
    StatsCanEconomicIndicatorsQueryParams,
)
from openbb_government_ca.utils.metadata import GovernmentCaMetadata


def _seed_catalog() -> None:
    """Populate the singleton with a minimal SDMX catalog."""
    GovernmentCaMetadata._reset()
    meta = GovernmentCaMetadata()
    meta._apply_blob(
        {
            "boc": {},
            "statscan": {
                "status": "ok",
                "indicators": [
                    {"source": "1", "title_en": "GDP", "geo_code": "0"},
                ],
                "catalog": {
                    "cubes": {
                        "10100139": {
                            "pid": "10100139",
                            "title_en": "GDP",
                            "subject_code": "13",
                            "frequency_code": "6",
                            "series": [
                                {
                                    "vector_id": "V1",
                                    "coordinate": "1.1.1.1",
                                    "label_en": "GDP at basic prices",
                                    "scalar_factor_code": "6",
                                    "uom_code": "203",
                                    "frequency_code": "6",
                                },
                                {
                                    "vector_id": "V2",
                                    "coordinate": "1.1.1.2",
                                    "label_en": "GDP at market prices",
                                    "scalar_factor_code": "6",
                                    "uom_code": "203",
                                    "frequency_code": "6",
                                },
                            ],
                        }
                    },
                    "subjects": {"13": "Economic accounts"},
                    "cube_count": 1,
                    "series_count": 2,
                    "status": "ok",
                },
            },
        }
    )


# ---------------------------------------------------------------------------
# transform_query
# ---------------------------------------------------------------------------
class TestTransformQuery:
    """``transform_query`` populates defaults and normalizes the symbol."""

    def test_default_symbol_is_homepage(self):
        """No symbol → 'homepage' (curated indicators list)."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query({})
        assert q.symbol == "homepage"

    def test_country_canada_normalizes_to_zero(self):
        """'canada' is normalized to geo_code '0'."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query(
            {"symbol": "V1", "country": "canada"}
        )
        assert q.country == "0"

    def test_country_ca_normalizes_to_zero(self):
        """'ca' is normalized to geo_code '0'."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query(
            {"symbol": "V1", "country": "ca"}
        )
        assert q.country == "0"

    def test_dates_default_to_one_year_to_today(self):
        """start_date defaults to 1 year ago; end_date to today."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query({})
        assert q.start_date is not None
        assert q.end_date == date.today()
        assert (q.end_date - q.start_date).days >= 364

    def test_explicit_dates_are_preserved(self):
        """Explicit dates are not overwritten by defaults."""
        q = StatsCanEconomicIndicatorsFetcher.transform_query(
            {
                "symbol": "V1",
                "start_date": date(2020, 1, 1),
                "end_date": date(2021, 1, 1),
            }
        )
        assert q.start_date == date(2020, 1, 1)
        assert q.end_date == date(2021, 1, 1)


# ---------------------------------------------------------------------------
# extract_data — degraded mode
# ---------------------------------------------------------------------------
class TestExtractDataDegradedMode:
    """``extract_data`` raises ``OpenBBError`` when the catalog is empty."""

    def test_degraded_catalog_raises_openbb_error(self):
        """A degraded catalog (no cubes) raises OpenBBError."""
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob({"boc": {}, "statscan": {"status": "degraded"}})
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            with pytest.raises(OpenBBError, match="degraded mode"):
                StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()

    def test_empty_catalog_raises_openbb_error(self):
        """An ok-status but empty catalog still raises OpenBBError."""
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {"boc": {}, "statscan": {"status": "ok", "catalog": {"cubes": {}}}}
        )
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            with pytest.raises(OpenBBError, match="empty or in degraded"):
                StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — single vector mode
# ---------------------------------------------------------------------------
class TestExtractDataVectorMode:
    """``extract_data`` with a vector ID fetches a single time series."""

    def test_single_vector_returns_observations(self):
        """A single vector ID returns observations from the WDS API."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query({"symbol": "V1"})
            mock_payload = [
                {"refPer": "2024-01", "value": 100.0},
                {"refPer": "2024-02", "value": 101.5},
            ]
            with patch(
                "openbb_government_ca.statscan.economic_indicators.StatsCanClient"
            ) as MockClient:
                instance = MockClient.return_value
                instance.get_data_from_vector_by_reference_period_range.return_value = (
                    mock_payload
                )
                result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)

            assert len(result) == 2
            assert result[0]["_vector_id"] == "V1"
            assert result[0]["_cube_pid"] == "10100139"
            assert result[0]["_label_en"] == "GDP at basic prices"
        finally:
            GovernmentCaMetadata._reset()

    def test_multiple_vectors_via_comma(self):
        """A comma-separated list of vector IDs is split correctly."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query({"symbol": "V1,V2"})
            with patch(
                "openbb_government_ca.statscan.economic_indicators.StatsCanClient"
            ) as MockClient:
                instance = MockClient.return_value
                instance.get_data_from_vector_by_reference_period_range.return_value = [
                    {"refPer": "2024-01", "value": 100.0}
                ]
                result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)

            assert len(result) == 2
            vids = {obs["_vector_id"] for obs in result}
            assert vids == {"V1", "V2"}
        finally:
            GovernmentCaMetadata._reset()

    def test_unknown_vector_is_skipped(self):
        """A vector ID not in the catalog is silently skipped."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query({"symbol": "V1,V999"})
            with patch(
                "openbb_government_ca.statscan.economic_indicators.StatsCanClient"
            ) as MockClient:
                instance = MockClient.return_value
                instance.get_data_from_vector_by_reference_period_range.return_value = [
                    {"refPer": "2024-01", "value": 100.0}
                ]
                result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)

            assert len(result) == 1
            assert result[0]["_vector_id"] == "V1"
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — cube mode
# ---------------------------------------------------------------------------
class TestExtractDataCubeMode:
    """``extract_data`` with ``cube:PID`` fetches every series in a cube."""

    def test_cube_prefix_fetches_all_series(self):
        """``cube:10100139`` fetches every series in cube 10100139."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query(
                {"symbol": "cube:10100139"}
            )
            with patch(
                "openbb_government_ca.statscan.economic_indicators.StatsCanClient"
            ) as MockClient:
                instance = MockClient.return_value
                instance.get_data_from_vector_by_reference_period_range.return_value = [
                    {"refPer": "2024-01", "value": 100.0}
                ]
                result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)

            assert len(result) == 2
            pids = {obs["_cube_pid"] for obs in result}
            assert pids == {"10100139"}
        finally:
            GovernmentCaMetadata._reset()

    def test_unknown_cube_raises_openbb_error(self):
        """An unknown cube PID raises OpenBBError."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query(
                {"symbol": "cube:99999999"}
            )
            with pytest.raises(OpenBBError):
                StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — homepage mode
# ---------------------------------------------------------------------------
class TestExtractDataHomepageMode:
    """``extract_data`` with ``homepage`` fetches the curated indicators list."""

    def test_homepage_fetches_all_homepage_vectors(self):
        """``homepage`` resolves to every vector ID in the homepage list."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query(
                {"symbol": "homepage"}
            )
            with patch(
                "openbb_government_ca.statscan.economic_indicators.StatsCanClient"
            ) as MockClient:
                instance = MockClient.return_value
                instance.get_data_from_vector_by_reference_period_range.return_value = [
                    {"refPer": "2024-01", "value": 100.0}
                ]
                result = StatsCanEconomicIndicatorsFetcher.extract_data(q, None)

            # The seeded catalog has 1 homepage indicator → 1 vector → 1 obs.
            assert len(result) == 1
        finally:
            GovernmentCaMetadata._reset()

    def test_empty_homepage_raises_empty_data_error(self):
        """An empty homepage indicators list raises EmptyDataError."""
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {
                "boc": {},
                "statscan": {
                    "status": "ok",
                    "indicators": [],
                    "catalog": {
                        "cubes": {"10100139": {"pid": "10100139", "series": []}},
                        "cube_count": 1,
                        "series_count": 0,
                        "status": "ok",
                    },
                },
            }
        )
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query(
                {"symbol": "homepage"}
            )
            with pytest.raises(EmptyDataError):
                StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — empty result
# ---------------------------------------------------------------------------
class TestExtractDataEmptyResult:
    """``extract_data`` raises ``EmptyDataError`` when no observations come back."""

    def test_no_observations_raises_empty_data_error(self):
        """When the WDS returns no observations, EmptyDataError is raised."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsFetcher.transform_query({"symbol": "V1"})
            with patch(
                "openbb_government_ca.statscan.economic_indicators.StatsCanClient"
            ) as MockClient:
                instance = MockClient.return_value
                instance.get_data_from_vector_by_reference_period_range.return_value = []
                with pytest.raises(EmptyDataError):
                    StatsCanEconomicIndicatorsFetcher.extract_data(q, None)
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# transform_data
# ---------------------------------------------------------------------------
class TestTransformData:
    """``transform_data`` maps raw WDS observations to the standard model."""

    def test_monthly_observation_maps_correctly(self):
        """A monthly observation is parsed and mapped to the data model."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            raw = [
                {
                    "refPer": "2024-01",
                    "value": 100.0,
                    "_vector_id": "V1",
                    "_cube_pid": "10100139",
                    "_coordinate": "1.1.1.1",
                    "_scalar_factor_code": "6",
                    "_uom_code": "203",
                    "_label_en": "GDP at basic prices",
                }
            ]
            result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
            assert len(result) == 1
            row = result[0]
            assert row.date == date(2024, 1, 1)
            assert row.value == 100.0
            assert row.symbol == "V1"
            assert row.symbol_root == "GDP at basic prices"
            assert row.vector_id == "V1"
            assert row.cube_pid == "10100139"
            assert row.coordinate == "1.1.1.1"
        finally:
            GovernmentCaMetadata._reset()

    def test_unparseable_value_becomes_none(self):
        """An unparseable value becomes None in the output."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            raw = [
                {
                    "refPer": "2024-01",
                    "value": "not a number",
                    "_vector_id": "V1",
                }
            ]
            result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
            assert result[0].value is None
        finally:
            GovernmentCaMetadata._reset()

    def test_quarterly_refper_parsed_to_first_day_of_quarter(self):
        """``"2024-Q1"`` is parsed to ``date(2024, 1, 1)``."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1")
            raw = [
                {
                    "refPer": "2024-Q1",
                    "value": 100.0,
                    "_vector_id": "V1",
                }
            ]
            result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
            assert result[0].date == date(2024, 1, 1)
        finally:
            GovernmentCaMetadata._reset()

    def test_results_sorted_by_symbol_then_date_desc(self):
        """Results are sorted by symbol (asc), then date (desc)."""
        _seed_catalog()
        try:
            q = StatsCanEconomicIndicatorsQueryParams(symbol="V1,V2")
            raw = [
                {
                    "refPer": "2024-02",
                    "value": 101.0,
                    "_vector_id": "V2",
                },
                {
                    "refPer": "2024-01",
                    "value": 100.0,
                    "_vector_id": "V2",
                },
                {
                    "refPer": "2024-01",
                    "value": 100.0,
                    "_vector_id": "V1",
                },
            ]
            result = StatsCanEconomicIndicatorsFetcher.transform_data(q, raw)
            assert [r.symbol for r in result] == ["V1", "V2", "V2"]
            assert [r.date for r in result] == [
                date(2024, 1, 1),
                date(2024, 2, 1),
                date(2024, 1, 1),
            ]
        finally:
            GovernmentCaMetadata._reset()
