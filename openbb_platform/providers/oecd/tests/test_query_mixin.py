"""Coverage tests for QueryMixin methods on OecdMetadata."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


class TestResolveDataflowTriplet:
    def test_returns_agency_full_id_version(self, seeded_meta):
        agency, full_id, version = seeded_meta.resolve_dataflow_triplet(_SHORT_ID)
        assert agency == "OECD"
        assert full_id == _FULL_ID
        assert version == "1.0"


class TestBuildDataUrl:
    def test_basic_url_shape(self, seeded_meta):
        url = seeded_meta.build_data_url(_SHORT_ID)
        assert "DSD_TEST%40DF_TEST" in url
        assert "dimensionAtObservation=TIME_PERIOD" in url
        assert "detail=dataonly" in url

    def test_last_n_appended(self, seeded_meta):
        url = seeded_meta.build_data_url(_SHORT_ID, last_n=5)
        assert "lastNObservations=5" in url

    def test_first_n_appended(self, seeded_meta):
        url = seeded_meta.build_data_url(_SHORT_ID, first_n=3)
        assert "firstNObservations=3" in url

    def test_last_n_blocked_for_blocked_dataflow(self, seeded_meta):
        blocked_full = "DSD_BATIS@DF_BATIS"
        seeded_meta.dataflows[blocked_full] = dict(seeded_meta.dataflows[_FULL_ID])
        seeded_meta.dataflows[blocked_full]["id"] = blocked_full
        seeded_meta.dataflows[blocked_full]["short_id"] = "DF_BATIS"
        seeded_meta._short_id_map["DF_BATIS"] = blocked_full
        seeded_meta.datastructures[blocked_full] = seeded_meta.datastructures[_FULL_ID]
        url = seeded_meta.build_data_url("DF_BATIS", last_n=5)
        assert "lastNObservations" not in url

    def test_last_n_blocked_for_blocked_agency(self, seeded_meta):
        seeded_meta.dataflows[_FULL_ID]["agency_id"] = "OECD.STI"
        url = seeded_meta.build_data_url(_SHORT_ID, last_n=5)
        assert "lastNObservations" not in url

    def test_no_time_dimension_skips_param(self, seeded_meta):
        seeded_meta.datastructures[_FULL_ID]["has_time_dimension"] = False
        url = seeded_meta.build_data_url(_SHORT_ID)
        assert "dimensionAtObservation" not in url


class TestBuildDimensionFilter:
    def test_default_all_wildcards(self, seeded_meta):
        result = seeded_meta.build_dimension_filter(_SHORT_ID)
        assert result == "*.*.*"

    def test_specific_dimensions(self, seeded_meta):
        result = seeded_meta.build_dimension_filter(_SHORT_ID, REF_AREA="USA", FREQ="A")
        parts = result.split(".")
        assert parts[0] == "USA"
        assert parts[1] == "*"
        assert parts[2] == "A"

    def test_empty_value_becomes_wildcard(self, seeded_meta):
        result = seeded_meta.build_dimension_filter(_SHORT_ID, REF_AREA="")
        assert result.split(".")[0] == "*"


class TestClassifyDimensions:
    def test_basic_classification(self, seeded_meta):
        result = seeded_meta.classify_dimensions(_SHORT_ID)
        country_ids = [d["id"] for d in result["country"]]
        freq_ids = [d["id"] for d in result["freq"]]
        assert "REF_AREA" in country_ids
        assert "FREQ" in freq_ids

    def test_time_period_excluded(self, seeded_meta):
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TIME_PERIOD",
                "position": 4,
                "codelist_id": "",
                "concept_id": "TIME_PERIOD",
                "name": "Time",
            }
        )
        result = seeded_meta.classify_dimensions(_SHORT_ID)
        assert all("TIME_PERIOD" not in [d["id"] for d in v] for v in result.values())

    def test_fixed_single_value_dim(self, seeded_meta):
        seeded_meta.codelists["OECD:CL_MEASURE(1.0)"] = {"CPI": "Consumer Price Index"}
        result = seeded_meta.classify_dimensions(_SHORT_ID)
        fixed_ids = [d["id"] for d in result["fixed"]]
        assert "MEASURE" in fixed_ids

    def test_axis_large_codelist(self, seeded_meta):
        seeded_meta.codelists["OECD:CL_MEASURE(1.0)"] = {
            f"C{i}": f"Code {i}" for i in range(60)
        }
        result = seeded_meta.classify_dimensions(_SHORT_ID)
        axis_ids = [d["id"] for d in result["axis"]]
        assert "MEASURE" in axis_ids

    def test_selector_role(self, seeded_meta):
        result = seeded_meta.classify_dimensions(_SHORT_ID)
        selector_ids = [d["id"] for d in result["selector"]]
        assert "MEASURE" in selector_ids

    def test_missing_codelist_returns_empty_values(self, seeded_meta):
        for dim in seeded_meta.datastructures[_FULL_ID]["dimensions"]:
            if dim["id"] == "MEASURE":
                dim["codelist_id"] = "UNKNOWN:NOPE(1.0)"
        result = seeded_meta.classify_dimensions(_SHORT_ID)
        measure = next(
            (d for v in result.values() for d in v if d["id"] == "MEASURE"), None
        )
        assert measure is not None
        assert measure["codelist_size"] == 0


class TestGetTableParameters:
    def test_returns_per_dim(self, seeded_meta):
        params = seeded_meta.get_table_parameters(_SHORT_ID)
        assert "REF_AREA" in params
        assert "FREQ" in params
        assert "MEASURE" in params

    def test_freq_default_picks_annual(self, seeded_meta):
        params = seeded_meta.get_table_parameters(_SHORT_ID)
        assert params["FREQ"]["default"] == "A"

    def test_freq_default_falls_back_to_first(self, seeded_meta):
        seeded_meta.codelists["OECD:CL_FREQ(1.0)"] = {"M": "Monthly", "Q": "Quarterly"}
        params = seeded_meta.get_table_parameters(_SHORT_ID)
        assert params["FREQ"]["default"] in {"M", "Q"}

    def test_freq_default_empty_codelist(self, seeded_meta):
        seeded_meta.codelists["OECD:CL_FREQ(1.0)"] = {}
        params = seeded_meta.get_table_parameters(_SHORT_ID)
        assert params["FREQ"]["default"] == "*"

    def test_fixed_default_picks_only_value(self, seeded_meta):
        seeded_meta.codelists["OECD:CL_MEASURE(1.0)"] = {"CPI": "Consumer Price Index"}
        params = seeded_meta.get_table_parameters(_SHORT_ID)
        assert params["MEASURE"]["default"] == "CPI"


class TestBuildTableQuery:
    def test_basic_default_query(self, seeded_meta):
        q = seeded_meta.build_table_query(_SHORT_ID)
        assert q.count(".") == 2

    def test_country_string_inserted(self, seeded_meta):
        q = seeded_meta.build_table_query(_SHORT_ID, country="USA")
        parts = q.split(".")
        assert parts[0] == "USA"

    def test_country_list_joined_with_plus(self, seeded_meta):
        q = seeded_meta.build_table_query(_SHORT_ID, country=["USA", "GBR"])
        assert "USA+GBR" in q

    def test_country_all_keyword_wildcard(self, seeded_meta):
        q = seeded_meta.build_table_query(_SHORT_ID, country="ALL")
        assert q.split(".")[0] == "*"

    def test_country_empty_string_wildcard(self, seeded_meta):
        q = seeded_meta.build_table_query(_SHORT_ID, country="")
        assert q.split(".")[0] == "*"

    def test_frequency_override(self, seeded_meta):
        q = seeded_meta.build_table_query(_SHORT_ID, frequency="Q")
        assert q.split(".")[2] == "Q"

    def test_selector_override(self, seeded_meta):
        q = seeded_meta.build_table_query(_SHORT_ID, MEASURE="PPI")
        assert "PPI" in q.split(".")

    def test_secondary_country_dim_becomes_wildcard(self, seeded_meta):
        seeded_meta.datastructures[_FULL_ID]["dimensions"].insert(
            1,
            {
                "id": "COUNTERPART_AREA",
                "position": 2,
                "codelist_id": "OECD:CL_AREA(1.0)",
                "concept_id": "REF_AREA",
                "name": "Counterpart Area",
            },
        )
        seeded_meta.datastructures[_FULL_ID]["dimensions"][2]["position"] = 3
        seeded_meta.datastructures[_FULL_ID]["dimensions"][3]["position"] = 4
        q = seeded_meta.build_table_query(_SHORT_ID, country="USA")
        parts = q.split(".")
        assert parts[0] == "USA"
        assert parts[1] == "*"

    def test_time_period_position_filled_with_wildcard(self, seeded_meta):
        seeded_meta.datastructures[_FULL_ID]["dimensions"].append(
            {
                "id": "TIME_PERIOD",
                "position": 4,
                "codelist_id": "",
                "concept_id": "TIME_PERIOD",
                "name": "Time",
            }
        )
        q = seeded_meta.build_table_query(_SHORT_ID)
        assert q.split(".")[3] == "*"

    def test_fixed_role_uses_default(self, seeded_meta):
        seeded_meta.codelists["OECD:CL_MEASURE(1.0)"] = {"CPI": "Consumer Price Index"}
        q = seeded_meta.build_table_query(_SHORT_ID)
        assert "CPI" in q.split(".")


class TestDescribeTableDimensions:
    def test_returns_one_entry_per_dimension(self, seeded_meta):
        rows = seeded_meta.describe_table_dimensions(_SHORT_ID)
        ids = {r["id"] for r in rows}
        assert {"REF_AREA", "MEASURE", "FREQ"} <= ids

    def test_includes_sample_values(self, seeded_meta):
        rows = seeded_meta.describe_table_dimensions(_SHORT_ID)
        ref_area = next(r for r in rows if r["id"] == "REF_AREA")
        assert ref_area["sample_values"]
        assert all("code" in s and "label" in s for s in ref_area["sample_values"])

    def test_empty_values_yield_empty_sample(self, seeded_meta):
        seeded_meta.codelists["OECD:CL_MEASURE(1.0)"] = {}
        rows = seeded_meta.describe_table_dimensions(_SHORT_ID)
        measure = next(r for r in rows if r["id"] == "MEASURE")
        assert measure["sample_values"] == []


class TestFetchAvailability:
    def _availability_response(self, **dim_values):
        return {
            "data": {
                "contentConstraints": [
                    {
                        "cubeRegions": [
                            {
                                "keyValues": [
                                    {"id": k, "values": v}
                                    for k, v in dim_values.items()
                                ]
                            }
                        ]
                    }
                ]
            }
        }

    def test_returns_cached_result_on_second_call(self, seeded_meta):
        sentinel = {"REF_AREA": ["USA"]}
        seeded_meta._availability_cache[f"{_FULL_ID}::"] = sentinel
        result = seeded_meta.fetch_availability(_SHORT_ID)
        assert result is sentinel

    def test_parses_availability_response(self, seeded_meta):
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._availability_response(
            REF_AREA=["USA", "GBR"], MEASURE=["CPI"]
        )
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            return_value=mock_resp,
        ):
            result = seeded_meta.fetch_availability(_SHORT_ID)
        assert result["REF_AREA"] == ["GBR", "USA"]
        assert result["MEASURE"] == ["CPI"]

    def test_fills_missing_dims_from_codelist(self, seeded_meta):
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._availability_response(REF_AREA=["USA"])
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            return_value=mock_resp,
        ):
            result = seeded_meta.fetch_availability(_SHORT_ID)
        assert "FREQ" in result
        assert "MEASURE" in result

    def test_pinned_dims_drive_cache_key(self, seeded_meta):
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._availability_response(REF_AREA=["USA"])
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            return_value=mock_resp,
        ):
            seeded_meta.fetch_availability(_SHORT_ID, pinned={"FREQ": "A"})
        keys = list(seeded_meta._availability_cache.keys())
        assert any("FREQ=A" in k for k in keys)

    def test_skips_time_period_in_keyvalues(self, seeded_meta):
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._availability_response(
            TIME_PERIOD=["2024"], REF_AREA=["USA"]
        )
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            return_value=mock_resp,
        ):
            result = seeded_meta.fetch_availability(_SHORT_ID)
        assert "TIME_PERIOD" not in result

    def test_request_error_falls_back_to_codelist(self, seeded_meta):
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            side_effect=RuntimeError("network down"),
        ):
            result = seeded_meta.fetch_availability(_SHORT_ID)
        assert "REF_AREA" in result
        assert "USA" in result["REF_AREA"]

    def test_request_error_uses_empty_when_no_codelist(self, seeded_meta, monkeypatch):
        for dim in seeded_meta.datastructures[_FULL_ID]["dimensions"]:
            dim["codelist_id"] = "UNKNOWN:X(1.0)"
        monkeypatch.setattr(
            type(seeded_meta),
            "_ensure_structure",
            lambda self, full_id, force=False: None,
        )
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            side_effect=RuntimeError("net"),
        ):
            result = seeded_meta.fetch_availability(_SHORT_ID)
        for v in result.values():
            assert v == []

    def test_constraints_filter_availability(self, seeded_meta):
        seeded_meta._dataflow_constraints[_FULL_ID] = {"REF_AREA": ["USA"]}
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._availability_response(
            REF_AREA=["USA", "GBR", "DEU"]
        )
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            return_value=mock_resp,
        ):
            result = seeded_meta.fetch_availability(_SHORT_ID)
        assert result["REF_AREA"] == ["USA"]

    def test_constraint_for_missing_dim_does_not_crash(self, seeded_meta):
        seeded_meta._dataflow_constraints[_FULL_ID] = {"NONEXISTENT": ["X"]}
        mock_resp = MagicMock()
        mock_resp.json.return_value = self._availability_response(REF_AREA=["USA"])
        with patch(
            "openbb_oecd.utils.metadata._query_mixin._make_request",
            return_value=mock_resp,
        ):
            result = seeded_meta.fetch_availability(_SHORT_ID)
        assert "REF_AREA" in result


@pytest.mark.parametrize(
    "agency,short,blocked",
    [
        ("OECD.STI", "DF_REGULAR", True),
        ("OECD.DCD", "DF_REGULAR", True),
        ("OECD", "DF_REGULAR", False),
    ],
)
def test_last_n_block_matrix(seeded_meta, agency, short, blocked):
    full_id = f"DSD_X@{short}"
    seeded_meta.dataflows[full_id] = dict(seeded_meta.dataflows[_FULL_ID])
    seeded_meta.dataflows[full_id]["id"] = full_id
    seeded_meta.dataflows[full_id]["short_id"] = short
    seeded_meta.dataflows[full_id]["agency_id"] = agency
    seeded_meta._short_id_map[short] = full_id
    seeded_meta.datastructures[full_id] = seeded_meta.datastructures[_FULL_ID]
    url = seeded_meta.build_data_url(short, last_n=10)
    if blocked:
        assert "lastNObservations" not in url
    else:
        assert "lastNObservations=10" in url
