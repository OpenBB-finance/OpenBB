"""Tests for ``openbb_government_ca.statscan.available_indicators``."""

from __future__ import annotations

from openbb_government_ca.statscan.available_indicators import (
    StatsCanAvailableIndicatorsData,
    StatsCanAvailableIndicatorsFetcher,
    StatsCanAvailableIndicatorsQueryParams,
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
                "indicators": [],
                "catalog": {
                    "cubes": {
                        "10100139": {
                            "pid": "10100139",
                            "title_en": "GDP at basic prices",
                            "subject_code": "13",
                            "frequency_code": "6",
                            "series": [
                                {
                                    "vector_id": "V1",
                                    "coordinate": "1.1.1.1",
                                    "label_en": "GDP, monthly",
                                    "scalar_factor_code": "6",
                                    "uom_code": "203",
                                    "frequency_code": "6",
                                },
                                {
                                    "vector_id": "V2",
                                    "coordinate": "1.1.1.2",
                                    "label_en": "GDP, quarterly",
                                    "scalar_factor_code": "6",
                                    "uom_code": "203",
                                    "frequency_code": "7",
                                },
                            ],
                        },
                        "20100008": {
                            "pid": "20100008",
                            "title_en": "CPI",
                            "subject_code": "14",
                            "frequency_code": "6",
                            "series": [
                                {
                                    "vector_id": "V3",
                                    "coordinate": "1.1.1.1",
                                    "label_en": "CPI All-items",
                                    "scalar_factor_code": "0",
                                    "uom_code": "200",
                                    "frequency_code": "6",
                                },
                            ],
                        },
                    },
                    "subjects": {
                        "13": "Economic accounts",
                        "14": "Consumer prices",
                    },
                    "cube_count": 2,
                    "series_count": 3,
                    "status": "ok",
                },
            },
        }
    )


# ---------------------------------------------------------------------------
# transform_query
# ---------------------------------------------------------------------------
class TestTransformQuery:
    """``transform_query`` accepts the documented parameters."""

    def test_default_query_has_no_filters(self):
        q = StatsCanAvailableIndicatorsFetcher.transform_query({})
        assert q.query is None
        assert q.cube_pid is None
        assert q.subject is None
        assert q.vector_id is None

    def test_query_passes_through(self):
        q = StatsCanAvailableIndicatorsFetcher.transform_query(
            {"query": "GDP", "cube_pid": "10100139"}
        )
        assert q.query == "GDP"
        assert q.cube_pid == "10100139"


# ---------------------------------------------------------------------------
# extract_data — vector_id mode
# ---------------------------------------------------------------------------
class TestExtractDataVectorId:
    """``extract_data`` with ``vector_id`` returns the matching series."""

    def test_single_vector_id(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(vector_id="V1")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert len(result) == 1
            assert result[0]["vector_id"] == "V1"
            assert result[0]["cube_pid"] == "10100139"
        finally:
            GovernmentCaMetadata._reset()

    def test_multiple_vector_ids_comma_separated(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(vector_id="V1,V3")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            vids = {r["vector_id"] for r in result}
            assert vids == {"V1", "V3"}
        finally:
            GovernmentCaMetadata._reset()

    def test_unknown_vector_id_returns_empty(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(vector_id="V999")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert result == []
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — cube_pid mode
# ---------------------------------------------------------------------------
class TestExtractDataCubePid:
    """``extract_data`` with ``cube_pid`` lists every series in the cube."""

    def test_single_cube_pid(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(cube_pid="10100139")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert len(result) == 2
            for row in result:
                assert row["cube_pid"] == "10100139"
        finally:
            GovernmentCaMetadata._reset()

    def test_multiple_cube_pids_comma_separated(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(cube_pid="10100139,20100008")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            pids = {r["cube_pid"] for r in result}
            assert pids == {"10100139", "20100008"}
        finally:
            GovernmentCaMetadata._reset()

    def test_unknown_cube_pid_returns_empty(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(cube_pid="99999999")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert result == []
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — subject mode
# ---------------------------------------------------------------------------
class TestExtractDataSubject:
    """``extract_data`` with ``subject`` lists every series under the subject."""

    def test_subject_filter(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(subject="13")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert len(result) == 2  # both series in cube 10100139
            for row in result:
                assert row["cube_pid"] == "10100139"
        finally:
            GovernmentCaMetadata._reset()

    def test_unknown_subject_returns_empty(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(subject="999")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert result == []
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — query mode (free-text search)
# ---------------------------------------------------------------------------
class TestExtractDataQuery:
    """``extract_data`` with ``query`` does a substring search on labels."""

    def test_query_match_returns_matching_series(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(query="GDP")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            # ``_series_to_row`` flattens label_en into both ``description``
            # and ``symbol_root``.
            labels = {r["description"] for r in result}
            assert "GDP, monthly" in labels
            assert "GDP, quarterly" in labels
            assert "CPI All-items" not in labels
        finally:
            GovernmentCaMetadata._reset()

    def test_query_no_match_returns_empty(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams(query="zzzznomatch")
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert result == []
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# extract_data — no filters returns everything
# ---------------------------------------------------------------------------
class TestExtractDataNoFilters:
    """Without any filter, every series in every cube is returned."""

    def test_no_filters_returns_all_series(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams()
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert len(result) == 3  # all series across both cubes
        finally:
            GovernmentCaMetadata._reset()

    def test_empty_catalog_returns_empty(self):
        GovernmentCaMetadata._reset()
        meta = GovernmentCaMetadata()
        meta._apply_blob(
            {"boc": {}, "statscan": {"status": "ok", "catalog": {"cubes": {}}}}
        )
        try:
            q = StatsCanAvailableIndicatorsQueryParams()
            result = StatsCanAvailableIndicatorsFetcher.extract_data(q, None)
            assert result == []
        finally:
            GovernmentCaMetadata._reset()


# ---------------------------------------------------------------------------
# transform_data
# ---------------------------------------------------------------------------
class TestTransformData:
    """``transform_data`` maps raw rows to ``StatsCanAvailableIndicatorsData``."""

    def test_transform_returns_pydantic_models(self):
        _seed_catalog()
        try:
            q = StatsCanAvailableIndicatorsQueryParams()
            raw = [
                {
                    "symbol": "V1",
                    "symbol_root": "GDP, monthly",
                    "vector_id": "V1",
                    "cube_pid": "10100139",
                    "cube_title": "GDP at basic prices",
                    "coordinate": "1.1.1.1",
                    "description": "GDP, monthly",
                    "frequency": "6",
                    "scalar_factor_code": "6",
                    "uom_code": "203",
                }
            ]
            result = StatsCanAvailableIndicatorsFetcher.transform_data(q, raw)
            assert len(result) == 1
            assert isinstance(result[0], StatsCanAvailableIndicatorsData)
            assert result[0].symbol == "V1"
            assert result[0].cube_pid == "10100139"
        finally:
            GovernmentCaMetadata._reset()
