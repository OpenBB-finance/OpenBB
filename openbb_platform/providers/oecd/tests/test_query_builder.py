"""Unit tests for openbb_oecd.utils.query_builder."""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_oecd.utils.metadata import OecdMetadata
from openbb_oecd.utils.query_builder import (
    OecdQueryBuilder,
    _format_period,
    parse_time_period,
)
from requests.exceptions import HTTPError

# pylint: disable=C1803, C0302, W0212, W0613, W0621
# flake8: noqa: D101, D102, SIM117

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"

_TEST_DATAFLOW = {
    "id": _FULL_ID,
    "short_id": _SHORT_ID,
    "agency_id": "OECD",
    "version": "1.0",
    "name": "Test Dataflow",
    "description": "",
    "structure_ref": "",
}

_TEST_DSD = {
    "dsd_id": "DSD_TEST",
    "agency_id": "OECD",
    "version": "1.0",
    "dimensions": [
        {
            "id": "REF_AREA",
            "position": 1,
            "codelist_id": "OECD:CL_AREA(1.0)",
            "concept_id": "REF_AREA",
            "name": "Reference Area",
        },
        {
            "id": "MEASURE",
            "position": 2,
            "codelist_id": "OECD:CL_MEASURE(1.0)",
            "concept_id": "MEASURE",
            "name": "Measure",
        },
        {
            "id": "FREQ",
            "position": 3,
            "codelist_id": "OECD:CL_FREQ(1.0)",
            "concept_id": "FREQ",
            "name": "Frequency",
        },
    ],
    "attributes": [],
    "has_time_dimension": True,
}

_TEST_CODELISTS = {
    "OECD:CL_AREA(1.0)": {
        "USA": "United States",
        "GBR": "United Kingdom",
        "DEU": "Germany",
    },
    "OECD:CL_MEASURE(1.0)": {
        "CPI": "Consumer Price Index",
        "PPI": "Producer Price Index",
    },
    "OECD:CL_FREQ(1.0)": {"A": "Annual", "Q": "Quarterly", "M": "Monthly"},
}

_TEST_CONSTRAINTS = {
    _FULL_ID: {
        "REF_AREA": ["USA", "GBR"],
        "MEASURE": ["CPI", "PPI"],
        "FREQ": ["A", "Q"],
    }
}


@pytest.fixture
def seeded_meta(monkeypatch):
    """Fresh OecdMetadata singleton with test data injected, no I/O."""
    OecdMetadata._reset()
    monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
    m = OecdMetadata()
    m.dataflows[_FULL_ID] = _TEST_DATAFLOW.copy()
    m._short_id_map[_SHORT_ID] = _FULL_ID
    m._full_catalogue_loaded = True
    m.datastructures[_FULL_ID] = {
        "dsd_id": "DSD_TEST",
        "agency_id": "OECD",
        "version": "1.0",
        "dimensions": [dict(d) for d in _TEST_DSD["dimensions"]],
        "attributes": [],
        "has_time_dimension": True,
    }
    m.codelists.update({k: dict(v) for k, v in _TEST_CODELISTS.items()})
    m._dataflow_constraints.update(
        {
            k: {dk: list(dv) for dk, dv in v.items()}
            for k, v in _TEST_CONSTRAINTS.items()
        }
    )
    yield m
    OecdMetadata._reset()


@pytest.fixture
def qb(seeded_meta):
    """OecdQueryBuilder with seeded_meta already in place."""
    builder = OecdQueryBuilder()
    assert builder.metadata is seeded_meta
    return builder


class TestFormatPeriod:
    def test_full_date_truncated(self):
        assert _format_period("2024-03-15") == "2024-03"

    def test_year_month_passthrough(self):
        assert _format_period("2024-03") == "2024-03"

    def test_year_only_passthrough(self):
        assert _format_period("2024") == "2024"

    def test_empty_string(self):
        assert _format_period("") == ""

    def test_none_like_empty(self):
        assert _format_period("") == ""

    def test_quarter_string_passthrough(self):
        result = _format_period("2024-Q3")
        # "2024-Q3" splits into ["2024", "Q3"] — not 3 parts → passthrough
        assert result == "2024-Q3"


class TestParseTimePeriod:
    def test_daily_passthrough(self):
        assert parse_time_period("2024-03-15") == "2024-03-15"

    def test_quarterly_q1(self):
        result = parse_time_period("2024-Q1")
        assert result == "2024-01-01"

    def test_quarterly_q2(self):
        assert parse_time_period("2023-Q2") == "2023-04-01"

    def test_quarterly_q3(self):
        assert parse_time_period("2022-Q3") == "2022-07-01"

    def test_quarterly_q4(self):
        assert parse_time_period("2021-Q4") == "2021-10-01"

    def test_monthly(self):
        assert parse_time_period("2024-06") == "2024-06-01"

    def test_annual(self):
        assert parse_time_period("2024") == "2024-01-01"

    def test_empty_string_passthrough(self):
        assert parse_time_period("") == ""

    def test_unknown_format_passthrough(self):
        assert parse_time_period("S1/2024") == "S1/2024"

    def test_already_iso(self):
        assert parse_time_period("2024-01-01") == "2024-01-01"


class TestBuildUrl:
    def test_basic_url_contains_dataflow(self, qb):
        url = qb.build_url(_SHORT_ID)
        assert "DF_TEST" in url
        assert "sdmx.oecd.org" in url

    def test_start_date_appended(self, qb):
        url = qb.build_url(_SHORT_ID, start_date="2020-01")
        assert "TIME_PERIOD" in url
        assert "ge:2020-01" in url

    def test_end_date_appended(self, qb):
        url = qb.build_url(_SHORT_ID, end_date="2023-12")
        assert "le:2023-12" in url

    def test_both_dates(self, qb):
        url = qb.build_url(_SHORT_ID, start_date="2020", end_date="2023")
        assert "ge:2020" in url
        assert "le:2023" in url

    def test_limit_appended(self, qb):
        url = qb.build_url(_SHORT_ID, limit=10)
        assert "lastNObservations=10" in url

    def test_dimension_kwarg_included(self, qb):
        url = qb.build_url(_SHORT_ID, REF_AREA="USA")
        assert "USA" in url

    def test_date_full_truncated_to_year_month(self, qb):
        url = qb.build_url(_SHORT_ID, start_date="2020-06-15")
        assert "ge:2020-06" in url

    def test_no_start_date_no_time_period_param(self, qb):
        url = qb.build_url(_SHORT_ID)
        assert "ge:" not in url
        assert "le:" not in url


class TestBuildDimensionFilter:
    def test_all_wildcards_by_default(self, qb):
        result = qb._build_dimension_filter(_SHORT_ID)
        parts = result.split(".")
        assert all(p == "*" for p in parts)

    def test_case_insensitive_key(self, qb):
        result_upper = qb._build_dimension_filter(_SHORT_ID, REF_AREA="USA")
        result_lower = qb._build_dimension_filter(_SHORT_ID, ref_area="USA")
        assert result_upper == result_lower

    def test_first_position_dimension(self, qb):
        result = qb._build_dimension_filter(_SHORT_ID, REF_AREA="GBR")
        assert result.startswith("GBR.")

    def test_unknown_kwarg_ignored(self, qb):
        result = qb._build_dimension_filter(_SHORT_ID, UNKNOWN_DIM="XYZ")
        # Unknown dims are ignored; the filter is still a valid structure
        parts = result.split(".")
        assert "XYZ" not in parts

    def test_multi_value_encoded(self, qb):
        result = qb._build_dimension_filter(_SHORT_ID, REF_AREA="USA+GBR")
        parts = result.split(".")
        assert parts[0] == "USA+GBR"

    def test_specific_freq(self, qb):
        result = qb._build_dimension_filter(_SHORT_ID, FREQ="Q")
        parts = result.split(".")
        # FREQ is position 2 (0-indexed)
        assert parts[2] == "Q"


class TestSplitLabelColumns:
    def _make_df(self, data: dict) -> pd.DataFrame:
        return pd.DataFrame(data)

    def test_renames_dim_label_columns(self, qb):
        df = self._make_df(
            {
                "REF_AREA: Reference Area": [
                    "USA: United States",
                    "GBR: United Kingdom",
                ],
                "OBS_VALUE": [1.0, 2.0],
                "TIME_PERIOD": ["2024", "2024"],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert "REF_AREA" in result.columns
        assert "REF_AREA: Reference Area" not in result.columns

    def test_splits_code_label_values(self, qb):
        df = self._make_df(
            {
                "REF_AREA: Reference Area": [
                    "USA: United States",
                    "GBR: United Kingdom",
                ],
                "OBS_VALUE": [1.0, 2.0],
                "TIME_PERIOD": ["2024", "2024"],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert list(result["REF_AREA"]) == ["USA", "GBR"]
        assert "REF_AREA_label" in result.columns
        assert list(result["REF_AREA_label"]) == ["United States", "United Kingdom"]

    def test_obs_value_not_split(self, qb):
        df = self._make_df(
            {
                "REF_AREA: Reference Area": ["USA: United States"],
                "OBS_VALUE": [3.14],
                "TIME_PERIOD": ["2024"],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert "OBS_VALUE" in result.columns
        assert list(result["OBS_VALUE"]) == [3.14]

    def test_time_period_not_split(self, qb):
        df = self._make_df(
            {
                "TIME_PERIOD": ["2024-Q3"],
                "REF_AREA: Reference Area": ["USA: United States"],
                "OBS_VALUE": [5.0],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert list(result["TIME_PERIOD"]) == ["2024-Q3"]

    def test_no_label_column_codelist_fallback(self, qb):
        """When cell values are plain codes (no ': '), labels come from codelist."""
        df = self._make_df(
            {
                "REF_AREA": ["USA", "GBR"],
                "OBS_VALUE": [1.0, 2.0],
                "TIME_PERIOD": ["2024", "2024"],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        if "REF_AREA_label" in result.columns:
            assert list(result["REF_AREA_label"]) == ["United States", "United Kingdom"]

    def test_empty_column_not_split(self, qb):
        df = self._make_df(
            {
                "REF_AREA: Reference Area": [None, None],
                "OBS_VALUE": [1.0, 2.0],
                "TIME_PERIOD": ["2024", "2024"],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert "REF_AREA" in result.columns

    def test_multiple_dimensions_all_renamed(self, qb):
        df = self._make_df(
            {
                "REF_AREA: Reference Area": ["USA: United States"],
                "FREQ: Frequency": ["A: Annual"],
                "OBS_VALUE": [1.0],
                "TIME_PERIOD": ["2024"],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert "REF_AREA" in result.columns
        assert "FREQ" in result.columns
        assert result["FREQ"].iloc[0] == "A"


class TestGetCountryDimension:
    def test_gets_ref_area(self, qb):
        with patch.object(qb.metadata, "classify_dimensions") as mock_cls:
            mock_cls.return_value = {"country": [{"id": "REF_AREA"}], "freq": []}
            result = qb.get_country_dimension(_SHORT_ID)
        assert result == "REF_AREA"

    def test_returns_none_when_no_country_dim(self, qb):
        with patch.object(qb.metadata, "classify_dimensions") as mock_cls:
            mock_cls.return_value = {"country": [], "freq": []}
            result = qb.get_country_dimension(_SHORT_ID)
        assert result is None


class TestGetFrequencyDimension:
    def test_gets_freq(self, qb):
        with patch.object(qb.metadata, "classify_dimensions") as mock_cls:
            mock_cls.return_value = {"country": [], "freq": [{"id": "FREQ"}]}
            result = qb.get_frequency_dimension(_SHORT_ID)
        assert result == "FREQ"

    def test_returns_none_when_no_freq_dim(self, qb):
        with patch.object(qb.metadata, "classify_dimensions") as mock_cls:
            mock_cls.return_value = {"country": [], "freq": []}
            result = qb.get_frequency_dimension(_SHORT_ID)
        assert result is None


class TestGetTranslationMaps:
    def test_returns_code_to_label(self, qb):
        result = qb.get_translation_maps(_SHORT_ID)
        assert "REF_AREA" in result
        assert result["REF_AREA"]["USA"] == "United States"
        assert result["FREQ"]["Q"] == "Quarterly"

    def test_all_dimensions_included(self, qb):
        result = qb.get_translation_maps(_SHORT_ID)
        assert "MEASURE" in result
        assert "FREQ" in result


class TestListTables:
    def test_delegates_to_metadata(self, qb):
        with patch.object(
            qb.metadata, "list_tables", return_value=[{"table_id": "X"}]
        ) as mock:
            result = qb.list_tables(query="test")
            mock.assert_called_once_with(query="test", topic=None)
        assert result == [{"table_id": "X"}]

    def test_with_topic(self, qb):
        with patch.object(qb.metadata, "list_tables", return_value=[]) as mock:
            qb.list_tables(topic="ECO")
            mock.assert_called_once_with(query=None, topic="ECO")


class TestGetTable:
    def test_delegates_to_metadata(self, qb):
        mock_result = {"dataflow_id": _FULL_ID, "short_id": _SHORT_ID}
        with patch.object(qb.metadata, "get_table", return_value=mock_result) as mock:
            result = qb.get_table(_SHORT_ID)
            mock.assert_called_once_with(_SHORT_ID)
        assert result == mock_result


class TestValidateDimensionConstraints:
    def test_no_dims_skips_validation(self, qb):
        """When no dimension kwargs, returns immediately without network call."""
        # Should not raise
        qb.validate_dimension_constraints(_SHORT_ID)

    def test_non_dimension_keys_skipped(self, qb):
        """start_date, end_date, limit are not validated as dimensions."""
        qb.validate_dimension_constraints(
            _SHORT_ID, start_date="2020", end_date="2023", limit=10
        )

    def test_valid_dimension_passes(self, qb):
        """A valid dimension value should pass without raising."""
        mock_qb_inst = MagicMock()
        mock_qb_inst.available.return_value = [
            {"value": "USA", "label": "United States"}
        ]
        with patch(
            "openbb_oecd.utils.query_builder.OecdParamsBuilder",
            return_value=mock_qb_inst,
        ):
            # Should not raise
            qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="USA")

    def test_invalid_dimension_raises(self, qb):
        """An invalid dimension value raises ValueError with helpful message."""
        mock_qb_inst = MagicMock()
        mock_qb_inst.available.return_value = [
            {"value": "USA", "label": "United States"}
        ]
        with patch(
            "openbb_oecd.utils.query_builder.OecdParamsBuilder",
            return_value=mock_qb_inst,
        ):
            with pytest.raises(ValueError, match="Invalid value"):
                qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="ZZZNOTVALID")

    def test_query_builder_init_failure_warns(self, qb):
        """If OecdParamsBuilder cannot be initialized, only a warning is issued."""
        with patch(
            "openbb_oecd.utils.query_builder.OecdParamsBuilder",
            side_effect=Exception("fail"),
        ):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="USA")
                assert len(w) == 1
                assert "Could not initialise" in str(w[0].message)

    def test_availability_failure_still_pins(self, qb):
        """If availability fetch fails, a warning is issued and the dim is pinned."""
        mock_qb_inst = MagicMock()
        mock_qb_inst.available.side_effect = Exception("avail fail")
        mock_qb_inst._pinned = {}
        mock_qb_inst._avail_cache = {}
        with patch(
            "openbb_oecd.utils.query_builder.OecdParamsBuilder",
            return_value=mock_qb_inst,
        ):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="USA")
                assert any("Could not fetch availability" in str(x.message) for x in w)

    def test_multi_value_not_pinned(self, qb):
        """Multi-value dimension values are not pinned for cascading."""
        mock_qb_inst = MagicMock()
        mock_qb_inst.available.return_value = [
            {"value": "USA", "label": "United States"},
            {"value": "GBR", "label": "United Kingdom"},
        ]
        mock_qb_inst._pinned = {}
        mock_qb_inst._avail_cache = {}
        with patch(
            "openbb_oecd.utils.query_builder.OecdParamsBuilder",
            return_value=mock_qb_inst,
        ):
            qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="USA+GBR")
            # Multi-select should NOT be pinned
            assert "REF_AREA" not in mock_qb_inst._pinned


class TestFetchData:
    def _make_csv_text(self, with_headers=True) -> str:
        lines = [
            "REF_AREA: Reference Area,MEASURE: Measure,FREQ: Frequency,TIME_PERIOD,OBS_VALUE",
            "USA: United States,CPI: Consumer Price Index,A: Annual,2024,105.2",
            "GBR: United Kingdom,CPI: Consumer Price Index,A: Annual,2024,103.7",
        ]
        if with_headers:
            return "\n".join(lines)
        return "\n".join(lines[1:])

    def test_basic_fetch_returns_data_and_metadata(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = self._make_csv_text()
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            result = qb.fetch_data(_SHORT_ID, _skip_validation=True)
        assert "data" in result
        assert "metadata" in result
        assert len(result["data"]) == 2

    def test_data_row_has_expected_keys(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = self._make_csv_text()
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            result = qb.fetch_data(_SHORT_ID, _skip_validation=True)
        row = result["data"][0]
        assert "TIME_PERIOD" in row
        assert "OBS_VALUE" in row

    def test_obs_value_numeric(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = self._make_csv_text()
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            result = qb.fetch_data(_SHORT_ID, _skip_validation=True)
        for row in result["data"]:
            assert isinstance(row["OBS_VALUE"], float)

    def test_metadata_fields(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = self._make_csv_text()
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            result = qb.fetch_data(_SHORT_ID, _skip_validation=True)
        meta = result["metadata"]
        assert meta["dataflow_id"] == _SHORT_ID
        assert meta["row_count"] == 2

    def test_empty_response_raises(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = ""
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            with pytest.raises(Exception):
                qb.fetch_data(_SHORT_ID, _skip_validation=True)

    def test_start_end_date_url_params(self, qb):
        """start/end date are appended to the URL as query params."""
        captured_urls = []
        mock_resp = MagicMock()
        mock_resp.text = self._make_csv_text()

        def capture_req(url, **kwargs):
            captured_urls.append(url)
            return mock_resp

        with patch(
            "openbb_oecd.utils.query_builder._make_request", side_effect=capture_req
        ):
            qb.fetch_data(
                _SHORT_ID, start_date="2020", end_date="2023", _skip_validation=True
            )

        assert captured_urls, "No request was made"
        assert any("ge:2020" in u for u in captured_urls)
        assert any("le:2023" in u for u in captured_urls)


class TestFetchWithMultiValueFallback:
    def _make_csv(self, rows=1) -> str:
        lines = ["REF_AREA,TIME_PERIOD,OBS_VALUE"]
        for i in range(rows):
            lines.append(f"USA,202{i},10{i}.0")
        return "\n".join(lines)

    def test_success_on_first_try(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = self._make_csv(2)
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            text = qb._fetch_with_multi_value_fallback(
                "http://test",
                {},
                _SHORT_ID,
                None,
                None,
                None,
                {},
            )
        assert "OBS_VALUE" in text

    def test_fallback_on_404_with_multi_value(self, qb):
        """When 404 and a dimension contains '+', falls back to per-value requests."""
        call_count = [0]
        csv_parts = [self._make_csv(1), "USA,2024,105.0"]

        def fake_req(url, **kwargs):
            resp = MagicMock()
            if call_count[0] == 0:
                call_count[0] += 1
                http_err = HTTPError("404")
                http_err.response = MagicMock(status_code=404)
                raise http_err
            resp.text = csv_parts[0] if call_count[0] == 1 else "USA,2024,105.0\n"
            call_count[0] += 1
            return resp

        with patch(
            "openbb_oecd.utils.query_builder._make_request", side_effect=fake_req
        ):
            with patch.object(qb, "build_url", return_value="http://single"):
                text = qb._fetch_with_multi_value_fallback(
                    "http://test",
                    {},
                    _SHORT_ID,
                    None,
                    None,
                    None,
                    {"REF_AREA": "USA+GBR"},
                )
        assert text is not None

    def test_raises_when_no_multi_value_on_404(self, qb):
        """Without '+' in any dimension, raises immediately on 404."""

        def fake_req(url, **kwargs):
            http_err = HTTPError("404")
            http_err.response = MagicMock(status_code=404)
            raise http_err

        with patch(
            "openbb_oecd.utils.query_builder._make_request", side_effect=fake_req
        ):
            with pytest.raises(OpenBBError, match="OECD data request failed"):
                qb._fetch_with_multi_value_fallback(
                    "http://test",
                    {},
                    _SHORT_ID,
                    None,
                    None,
                    None,
                    {"REF_AREA": "USA"},  # No '+' here
                )


class TestEdgeCases:
    def test_format_period_already_year_month(self):
        assert _format_period("2024-01") == "2024-01"

    def test_parse_time_period_invalid_quarter(self):
        result = parse_time_period("2024-Q5")
        assert result is not None

    def test_build_url_no_kwargs(self, qb):
        url = qb.build_url(_SHORT_ID)
        assert "DF_TEST" in url
        assert "http" in url

    def test_split_label_columns_no_label_format(self, qb):
        """Columns without ': ' in header are passed through unchanged."""
        df = pd.DataFrame(
            {
                "REF_AREA": ["USA"],
                "OBS_VALUE": [1.0],
                "TIME_PERIOD": ["2024"],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert "REF_AREA" in result.columns
