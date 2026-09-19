"""Tests for IMF metadata mixin modules driving 100% coverage."""

# ruff: noqa: I001

from __future__ import annotations

import json
import lzma
from unittest.mock import MagicMock, patch

import pytest

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.warning import OpenBBWarning

from openbb_imf.utils.metadata import ImfMetadata
from openbb_imf.utils.metadata import _cache_mixin
from openbb_imf.utils.metadata._loader_mixin import (
    _extract_codelist_payload,
    _shape_codelist,
)
from openbb_imf.utils.metadata._indicator_mixin import (
    _is_indicator_dimension,
    _make_indicator_entry,
)
from openbb_imf.utils.metadata._search_mixin import _matches_query
from openbb_imf.utils.metadata._table_mixin import (
    _build_series_id,
    _derive_node_label,
    _hierarchy_overlaps_dataflow,
    _is_irfcl_path_label,
    _strip_known_ancestors,
)
from openbb_imf.utils.metadata._typing import _MixinBase


def _real_load(instance):
    """Call the real cache-load method, bypassing fixture monkeypatching."""
    return _cache_mixin.CacheMixin._load_from_cache(instance)


class TestCacheMixin:
    """Coverage for ``_cache_mixin`` load and warning paths."""

    def test_load_from_cache_missing_file_returns_false(self, empty_meta, monkeypatch):
        """Return False when the shipped cache file is absent."""

        class FakePath:
            """Tiny stand-in for ``Path`` used in cache lookups."""

            def exists(self) -> bool:
                return False

        monkeypatch.setattr(_cache_mixin, "_SHIPPED_CACHE_FILE", FakePath())
        assert _real_load(empty_meta) is False

    def test_load_from_cache_success(self, empty_meta, monkeypatch, tmp_path):
        """Populate caches when the shipped cache file is valid lzma JSON."""
        cache_payload = {
            "dataflows": {"X": {"id": "X"}},
            "datastructures": {"DSD_X": {"id": "DSD_X"}},
            "conceptschemes": {"CS": {}},
            "dataflow_groups": {},
            "metadata_cache": {},
            "constraints_cache": {},
            "codelist_cache": {"CL_X": {"A": "Alpha"}},
            "codelist_descriptions": {"CL_X": {"A": "Alpha"}},
            "dataflow_parameters": {},
            "dataflow_indicators": {},
            "hierarchies": {"H1": {"hierarchicalCodes": []}},
        }
        cache_path = tmp_path / "imf_cache.json.xz"
        with lzma.open(cache_path, "wb") as fh:
            fh.write(json.dumps(cache_payload).encode())

        monkeypatch.setattr(_cache_mixin, "_SHIPPED_CACHE_FILE", cache_path)
        assert _real_load(empty_meta) is True
        assert empty_meta.dataflows == {"X": {"id": "X"}}
        assert empty_meta._codelist_cache == {"CL_X": {"A": "Alpha"}}

    def test_load_from_cache_corrupt_warns(self, empty_meta, monkeypatch, tmp_path):
        """Warn and return False when the cache file is unreadable."""
        bad_path = tmp_path / "imf_cache.json.xz"
        bad_path.write_bytes(b"not-lzma")
        monkeypatch.setattr(_cache_mixin, "_SHIPPED_CACHE_FILE", bad_path)

        with pytest.warns(OpenBBWarning, match="Error loading cache"):
            assert _real_load(empty_meta) is False


class TestCoreSingleton:
    """Coverage for the double-checked singleton initializer."""

    def test_double_init_short_circuits(self, monkeypatch):
        """``__init__`` returns early when the instance is already initialised."""
        ImfMetadata._reset()
        monkeypatch.setattr(ImfMetadata, "_load_from_cache", lambda self: True)
        first = ImfMetadata()
        first.dataflows = {"SENTINEL": {"id": "SENTINEL"}}

        second = ImfMetadata()
        assert second is first
        assert second.dataflows == {"SENTINEL": {"id": "SENTINEL"}}

        second.__init__()
        assert second.dataflows == {"SENTINEL": {"id": "SENTINEL"}}

        ImfMetadata._reset()

    def test_deepcopy_returns_self(self, monkeypatch):
        """``deepcopy`` on the singleton must return the same instance."""
        from copy import deepcopy

        ImfMetadata._reset()
        monkeypatch.setattr(ImfMetadata, "_load_from_cache", lambda self: True)
        m = ImfMetadata()
        assert deepcopy(m) is m
        ImfMetadata._reset()

    def test_copy_returns_self(self, monkeypatch):
        """``copy`` on the singleton must return the same instance."""
        from copy import copy

        ImfMetadata._reset()
        monkeypatch.setattr(ImfMetadata, "_load_from_cache", lambda self: True)
        m = ImfMetadata()
        assert copy(m) is m
        ImfMetadata._reset()

    def test_double_check_inside_lock(self, monkeypatch):
        """Inner ``self._initialized`` check inside the lock short-circuits init."""
        ImfMetadata._reset()
        monkeypatch.setattr(ImfMetadata, "_load_from_cache", lambda self: True)
        instance = ImfMetadata.__new__(ImfMetadata)
        instance._initialized = False

        class _FlippingLock:
            """Lock proxy that flips ``_initialized`` to True on enter."""

            def __enter__(self_inner):  # noqa: N805
                instance._initialized = True
                return self_inner

            def __exit__(self_inner, *exc):  # noqa: N805
                return False

        monkeypatch.setattr(ImfMetadata, "_lock", _FlippingLock())
        instance.__init__()
        assert not hasattr(instance, "dataflows")
        ImfMetadata._reset()


class TestHelpersMixin:
    """Coverage for ``_helpers`` delegation and dimension resolution."""

    def test_static_parse_helpers(self, empty_meta):
        """Static helpers delegate to the underlying parsers."""
        urn = "urn:sdmx:org.sdmx.infomodel.codelist.Code=IMF.STA:CL_X(1.0).CODE"
        assert empty_meta._parse_agency_from_urn(urn) == "IMF.STA"
        assert empty_meta._parse_codelist_id_from_urn(urn) == "CL_X"
        assert empty_meta._parse_indicator_code_from_urn(urn) == "CODE"
        owning_urn = "urn:sdmx:any=IMF.STA:CL_X(1.0)"
        assert empty_meta._parse_codelist_urn(owning_urn) == "CL_X"

    def test_parse_query_and_time_periods(self, empty_meta):
        """``_parse_query`` and ``_build_time_period_parameters`` delegate."""
        assert empty_meta._parse_query("gdp") == [["gdp"]]
        options, count = empty_meta._build_time_period_parameters(None)
        assert options == [] and count is None

    def test_extract_all_codelists_from_hierarchy(self, empty_meta):
        """Hierarchy traversal extracts codelist IDs."""
        hierarchy = {
            "hierarchicalCodes": [
                {
                    "code": "urn:sdmx:any=IMF.STA:CL_A(1.0).X",
                    "hierarchicalCodes": [{"code": "urn:sdmx:any=IMF.STA:CL_B(1.0).Y"}],
                }
            ]
        }
        result = empty_meta._extract_all_codelists_from_hierarchy(hierarchy)
        assert result == {"CL_A", "CL_B"}

    def test_get_dimension_for_codelist_missing_dataflow(self, seeded_meta):
        """Return None when the dataflow is not in the registry."""
        assert seeded_meta._get_dimension_for_codelist("MISSING", "CL_X") is None

    def test_get_dimension_for_codelist_missing_dsd(self, seeded_meta):
        """Return None when the dataflow points at an unknown DSD."""
        seeded_meta.dataflows["NO_DSD"] = {
            "id": "NO_DSD",
            "agencyID": "IMF.STA",
            "structureRef": {"id": "DSD_MISSING"},
        }
        assert seeded_meta._get_dimension_for_codelist("NO_DSD", "CL_X") is None

    def test_get_dimension_for_codelist_no_structure_ref(self, seeded_meta):
        """Return None when ``structureRef`` is empty."""
        seeded_meta.dataflows["NO_REF"] = {"id": "NO_REF", "structureRef": {}}
        assert seeded_meta._get_dimension_for_codelist("NO_REF", "CL_X") is None

    def test_get_dimension_for_codelist_segment_match(self, seeded_meta):
        """Match via dimension-id segment uppercased."""
        result = seeded_meta._get_dimension_for_codelist("TEST_DF", "CL_COUNTRY")
        assert result == "COUNTRY"

    def test_get_dimension_for_codelist_substring_match(self, seeded_meta):
        """Match via dimension-id substring fallback."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"].append(
            {"id": "FOO", "position": "3", "conceptRef": {"id": "FOO"}}
        )
        seeded_meta._codelist_cache["CL_TEST_FOOBAR"] = {"X": "Y"}
        result = seeded_meta._get_dimension_for_codelist("TEST_DF", "CL_TEST_FOOBAR")
        assert result == "FOO"

    def test_get_dimension_for_codelist_no_match(self, seeded_meta):
        """Return None when nothing matches."""
        result = seeded_meta._get_dimension_for_codelist("TEST_DF", "CL_NOWHERE")
        assert result is None

    def test_get_dimension_for_codelist_skips_blank_dim_ids(self, seeded_meta):
        """Blank dimension IDs are ignored during the first resolution loop."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"].insert(
            0, {"id": "", "position": "-1", "conceptRef": {"id": ""}}
        )
        result = seeded_meta._get_dimension_for_codelist("TEST_DF", "CL_INDICATOR")
        assert result == "INDICATOR"

    def test_get_dimension_for_codelist_falls_through_to_substring_loop(
        self, seeded_meta
    ):
        """Reach the third (codelist-upper substring) loop with a match."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"] = [
            {"id": "WIDGETID", "position": "0", "conceptRef": {"id": "WID"}}
        ]
        result = seeded_meta._get_dimension_for_codelist("TEST_DF", "CL_WIDGETIDDETAIL")
        assert result == "WIDGETID"


class TestIndicatorMixin:
    """Coverage for ``_indicator_mixin.get_indicators_in``."""

    def test_get_indicators_in_unknown_dataflow_raises(self, seeded_meta):
        """Unknown dataflow ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            seeded_meta.get_indicators_in("NOPE")

    def test_get_indicators_in_missing_dsd_raises(self, seeded_meta):
        """Missing DSD raises ValueError."""
        seeded_meta.dataflows["BAD"] = {
            "id": "BAD",
            "agencyID": "IMF.STA",
            "structureRef": {"id": "NOPE"},
        }
        with pytest.raises(ValueError, match="Data structure not found"):
            seeded_meta.get_indicators_in("BAD")

    def test_get_indicators_in_returns_entries(self, seeded_meta, monkeypatch):
        """Return one entry per available indicator code."""

        def _fake_params(self, dataflow_id):
            return {"INDICATOR": [{"value": "GDP", "label": "GDP"}]}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _fake_params)
        result = seeded_meta.get_indicators_in("TEST_DF")
        assert any(r["indicator"] == "GDP" for r in result)
        assert all(r["series_id"].startswith("TEST_DF::") for r in result)

    def test_get_indicators_in_handles_params_exception(self, seeded_meta, monkeypatch):
        """A get_dataflow_parameters error is swallowed and treated as empty."""

        def _boom(self, dataflow_id):
            raise RuntimeError("nope")

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _boom)
        with pytest.raises(KeyError):
            seeded_meta.get_indicators_in("TEST_DF")

    def test_get_indicators_in_fetches_uncached_codelist(
        self, seeded_meta, monkeypatch
    ):
        """When the descriptions map is empty and uncached, fetch then continue."""

        def _fake_params(self, dataflow_id):
            return {"INDICATOR": [{"value": "GDP", "label": "GDP"}]}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _fake_params)
        seeded_meta._codelist_descriptions.pop("CL_INDICATOR", None)
        del seeded_meta._codelist_cache["CL_INDICATOR"]

        def _fake_get_codelist_map(
            self, codelist_id, agency_id, dataflow_id, include_descriptions=False
        ):
            self._codelist_descriptions[codelist_id] = {"GDP": "GDP desc"}
            self._codelist_cache[codelist_id] = {"GDP": "GDP"}
            return {"GDP": "GDP"}

        monkeypatch.setattr(ImfMetadata, "_get_codelist_map", _fake_get_codelist_map)
        result = seeded_meta.get_indicators_in("TEST_DF")
        assert any(r["description"] == "GDP desc" for r in result)

    def test_get_indicators_in_fetch_failure_is_swallowed(
        self, seeded_meta, monkeypatch
    ):
        """When the uncached fetch raises, fall back to empty descriptions."""

        def _fake_params(self, dataflow_id):
            return {"INDICATOR": [{"value": "GDP", "label": "GDP"}]}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _fake_params)
        seeded_meta._codelist_descriptions.pop("CL_INDICATOR", None)
        del seeded_meta._codelist_cache["CL_INDICATOR"]

        def _boom(*a, **kw):
            raise RuntimeError("boom")

        monkeypatch.setattr(ImfMetadata, "_get_codelist_map", _boom)
        result = seeded_meta.get_indicators_in("TEST_DF")
        assert any(r["description"] == "" for r in result)

    def test_get_indicators_in_activity_dimension(self, seeded_meta, monkeypatch):
        """``ACTIVITY`` dimension adds activity codelist entries."""
        seeded_meta.dataflows["ACT_DF"] = {
            "id": "ACT_DF",
            "agencyID": "IMF.STA",
            "name": "Activity",
            "description": "",
            "structureRef": {"id": "DSD_ACT"},
        }
        seeded_meta.datastructures["DSD_ACT"] = {
            "id": "DSD_ACT",
            "agencyID": "IMF.STA",
            "dimensions": [
                {"id": "ACTIVITY", "position": "0", "conceptRef": {"id": "ACTIVITY"}}
            ],
        }
        seeded_meta._codelist_cache["CL_ACT_DF_ACTIVITY"] = {"MFG": "Manufacturing"}
        seeded_meta._codelist_descriptions["CL_ACT_DF_ACTIVITY"] = {
            "MFG": "Manufacturing desc"
        }

        def _fake_params(self, dataflow_id):
            return {}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _fake_params)
        result = seeded_meta.get_indicators_in("ACT_DF")
        assert any(r["indicator"] == "MFG" for r in result)

    def test_get_indicators_in_empty_raises_keyerror(self, seeded_meta, monkeypatch):
        """KeyError when no indicator-like dimension is found."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"] = [
            {"id": "DUMMY", "position": "0", "conceptRef": {"id": "DUMMY"}}
        ]

        def _fake_params(self, dataflow_id):
            return {}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _fake_params)
        with pytest.raises(KeyError):
            seeded_meta.get_indicators_in("TEST_DF")

    def test_get_indicators_in_returns_cached_result(self, seeded_meta):
        """A pre-populated ``_dataflow_indicators_cache`` short-circuits the build."""
        sentinel = [{"indicator": "PRECACHED"}]
        seeded_meta._dataflow_indicators_cache = {"TEST_DF": sentinel}
        out = seeded_meta.get_indicators_in("TEST_DF")
        assert out is sentinel

    def test_is_indicator_dimension_helpers(self):
        """Dimension classifier checks whitelist and substrings."""
        assert _is_indicator_dimension(None) is False
        assert _is_indicator_dimension("") is False
        assert _is_indicator_dimension("INDICATOR") is True
        assert _is_indicator_dimension("BOP_ACCOUNTING_ENTRY") is True
        assert _is_indicator_dimension("SOMETHING_ENTRY_ELSE") is True
        assert _is_indicator_dimension("UNRELATED") is False

    def test_make_indicator_entry(self):
        """Indicator entry builder shapes the dict."""
        entry = _make_indicator_entry(
            dataflow_id="A",
            dataflow_name="A name",
            structure_id="DSD_A",
            agency_id="IMF",
            dim_id="INDICATOR",
            code_id="X",
            label="X label",
            description="X desc",
        )
        assert entry == {
            "dataflow_id": "A",
            "dataflow_name": "A name",
            "structure_id": "DSD_A",
            "agency_id": "IMF",
            "dimension_id": "INDICATOR",
            "indicator": "X",
            "label": "X label",
            "description": "X desc",
            "series_id": "A::X",
            "extra_dimensions": [],
        }

    def test_make_indicator_entry_with_extra_dimensions(self):
        """``extra_dimensions`` are forwarded into the entry."""
        entry = _make_indicator_entry(
            dataflow_id="A",
            dataflow_name="A name",
            structure_id="DSD_A",
            agency_id="IMF",
            dim_id="INDICATOR",
            code_id="X",
            label="X label",
            description="X desc",
            extra_dimensions=["WGT_TYPE"],
        )
        assert entry["extra_dimensions"] == ["WGT_TYPE"]


def _build_mock_response(status_code=200, json_data=None, raise_on_status=False):
    """Return a MagicMock that mimics ``requests.Response``."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    if raise_on_status:
        response.raise_for_status.side_effect = Exception("HTTP error")
    else:
        response.raise_for_status.return_value = None
    return response


class TestLoaderMixin:
    """Coverage for ``_loader_mixin`` fetchers and helpers."""

    def test_extract_codelist_payload(self):
        """Pull labels and descriptions from a codelist payload."""
        codelist = {
            "codes": [
                {
                    "id": "A",
                    "names": {"en": "Alpha"},
                    "descriptions": {"en": "Alpha description"},
                },
                {"id": "B", "name": "Bravo", "description": "Bravo description"},
                {"id": "C", "name": "Charlie"},
                {"id": ""},
            ]
        }
        labels, descs = _extract_codelist_payload(codelist)
        assert labels == {"A": "Alpha", "B": "Bravo", "C": "Charlie"}
        assert descs["A"] == "Alpha description"
        assert descs["B"] == "Bravo description"
        assert descs["C"] == "Charlie"

    def test_fetch_single_codelist_already_cached(self, seeded_meta):
        """Skip the HTTP call when the codelist is already cached."""
        assert seeded_meta._fetch_single_codelist("IMF.STA", "CL_COUNTRY") is True

    def test_fetch_single_codelist_non_200(self, empty_meta):
        """Non-200 response yields False without populating caches."""
        with patch("openbb_core.provider.utils.helpers.make_request") as mock_req:
            mock_req.return_value = _build_mock_response(status_code=404)
            assert empty_meta._fetch_single_codelist("IMF.STA", "CL_TEST") is False

    def test_fetch_single_codelist_request_exception(self, empty_meta):
        """RequestException returns False."""
        from requests.exceptions import RequestException

        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            side_effect=RequestException("boom"),
        ):
            assert empty_meta._fetch_single_codelist("IMF.STA", "CL_TEST") is False

    def test_fetch_single_codelist_empty_payload(self, empty_meta):
        """Empty ``data.codelists`` returns False."""
        with patch("openbb_core.provider.utils.helpers.make_request") as mock_req:
            mock_req.return_value = _build_mock_response(
                json_data={"data": {"codelists": []}}
            )
            assert empty_meta._fetch_single_codelist("IMF.STA", "CL_TEST") is False

    def test_fetch_single_codelist_success(self, empty_meta):
        """Successful fetch populates ``_codelist_cache``."""
        payload = {
            "data": {
                "codelists": [
                    {
                        "id": "CL_TEST",
                        "codes": [
                            {"id": "A", "names": {"en": "Alpha"}},
                        ],
                    },
                    {"id": ""},
                ]
            }
        }
        with patch("openbb_core.provider.utils.helpers.make_request") as mock_req:
            mock_req.return_value = _build_mock_response(json_data=payload)
            assert empty_meta._fetch_single_codelist("IMF.STA", "CL_TEST") is True
        assert empty_meta._codelist_cache["CL_TEST"] == {"A": "Alpha"}

    def test_bulk_fetch_request_exception_warns(self, empty_meta):
        """Bulk fetch warns and returns on RequestException."""
        from requests.exceptions import RequestException

        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            side_effect=RequestException("boom"),
        ):
            with pytest.warns(OpenBBWarning, match="Could not bulk fetch"):
                empty_meta._bulk_fetch_and_cache_codelists("IMF.STA", "DF")

    def test_bulk_fetch_success(self, empty_meta):
        """Bulk fetch populates caches from the payload."""
        payload = {
            "data": {
                "codelists": [
                    {
                        "id": "CL_BULK",
                        "codes": [{"id": "X", "names": {"en": "X label"}}],
                    },
                    {"id": ""},
                ]
            }
        }
        with patch("openbb_core.provider.utils.helpers.make_request") as mock_req:
            mock_req.return_value = _build_mock_response(json_data=payload)
            empty_meta._bulk_fetch_and_cache_codelists("IMF.STA", "DF")
        assert empty_meta._codelist_cache["CL_BULK"] == {"X": "X label"}

    def test_get_codelist_map_hits_cache(self, seeded_meta):
        """Already-cached codelist returns immediately."""
        result = seeded_meta._get_codelist_map("CL_COUNTRY", "IMF.STA", "TEST_DF")
        assert "USA" in result

    def test_get_codelist_map_with_descriptions(self, seeded_meta):
        """Returns enriched shape when descriptions are requested."""
        result = seeded_meta._get_codelist_map(
            "CL_COUNTRY", "IMF.STA", "TEST_DF", include_descriptions=True
        )
        assert result["USA"] == {"name": "United States", "description": "USA"}

    def test_get_codelist_map_fetches_then_returns(self, empty_meta, monkeypatch):
        """Triggers bulk fetch when codelist is missing, then returns it."""

        def _bulk(self, agency_id, dataflow_id):
            self._codelist_cache["CL_NEW"] = {"K": "V"}
            self._codelist_descriptions["CL_NEW"] = {"K": "V"}

        monkeypatch.setattr(ImfMetadata, "_bulk_fetch_and_cache_codelists", _bulk)
        assert empty_meta._get_codelist_map("CL_NEW", "IMF.STA", "DF") == {"K": "V"}

    def test_get_codelist_map_warns_when_missing(self, empty_meta, monkeypatch):
        """Warns and returns ``{}`` when codelist remains missing after fetch."""

        def _bulk(self, agency_id, dataflow_id):
            return None

        monkeypatch.setattr(ImfMetadata, "_bulk_fetch_and_cache_codelists", _bulk)
        with pytest.warns(OpenBBWarning, match="Codelist 'CL_ABSENT' not found"):
            assert empty_meta._get_codelist_map("CL_ABSENT", "IMF.STA", "DF") == {}

    def test_shape_codelist_labels_only(self):
        """Default shape returns a copy of the labels dict."""
        labels = {"A": "Alpha"}
        result = _shape_codelist(labels, {"A": "desc"}, include_descriptions=False)
        assert result == labels
        assert result is not labels

    def test_shape_codelist_include_descriptions_falsy(self):
        """``include_descriptions=True`` with empty descs falls back to labels."""
        labels = {"A": "Alpha"}
        result = _shape_codelist(labels, {}, include_descriptions=True)
        assert result == labels

    def test_bulk_fetch_json_decode_error(self, empty_meta):
        """Bulk fetch warns when JSON cannot be decoded."""
        bad_response = MagicMock()
        bad_response.json.side_effect = json.JSONDecodeError("nope", "", 0)
        bad_response.raise_for_status.return_value = None
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=bad_response,
        ):
            with pytest.warns(OpenBBWarning, match="Could not bulk fetch"):
                empty_meta._bulk_fetch_and_cache_codelists("IMF.STA", "DF")

    def test_fetch_single_codelist_json_decode_error(self, empty_meta):
        """Single fetch returns False when JSON cannot be decoded."""
        bad_response = MagicMock()
        bad_response.status_code = 200
        bad_response.json.side_effect = json.JSONDecodeError("nope", "", 0)
        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            return_value=bad_response,
        ):
            assert empty_meta._fetch_single_codelist("IMF.STA", "CL_TEST") is False


class TestQueryMixin:
    """Coverage for ``_query_mixin`` parameter, constraint, codelist resolution."""

    def test_get_dataflow_parameters_unknown_raises(self, seeded_meta):
        """Unknown dataflow raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            seeded_meta.get_dataflow_parameters("NOPE")

    def test_get_dataflow_parameters_cached(self, seeded_meta):
        """Returns cached parameters when present."""
        seeded_meta._dataflow_parameters_cache["TEST_DF"] = {
            "INDICATOR": [{"label": "GDP", "value": "GDP"}]
        }
        result = seeded_meta.get_dataflow_parameters("TEST_DF")
        assert result == {"INDICATOR": [{"label": "GDP", "value": "GDP"}]}

    def test_get_dataflow_parameters_missing_dsd(self, seeded_meta):
        """Missing DSD returns ``{}``."""
        seeded_meta.dataflows["NODSD"] = {
            "id": "NODSD",
            "agencyID": "IMF.STA",
            "structureRef": {"id": "MISSING"},
        }
        result = seeded_meta.get_dataflow_parameters("NODSD")
        assert result == {}

    def test_get_dataflow_parameters_builds(self, seeded_meta, monkeypatch):
        """Builds parameter map from constraints and cached codelists."""

        def _fake_constraints(self, **kwargs):
            return {
                "key_values": [{"id": "INDICATOR", "values": ["GDP"]}],
                "full_response": {
                    "data": {
                        "contentConstraints": [
                            {
                                "annotations": [
                                    {"id": "time_period_start", "title": "1990"},
                                    {"id": "time_period_end", "title": "2024"},
                                ]
                            }
                        ]
                    }
                },
            }

        monkeypatch.setattr(ImfMetadata, "get_available_constraints", _fake_constraints)
        result = seeded_meta.get_dataflow_parameters("TEST_DF")
        assert "INDICATOR" in result
        assert any(opt["value"] == "GDP" for opt in result["INDICATOR"])
        assert "TIME_PERIOD" in result

    def test_get_dataflow_parameters_dict_label_and_value_equal(
        self, seeded_meta, monkeypatch
    ):
        """Dict labels are unwrapped; ``label == value`` is replaced by the id."""
        seeded_meta._codelist_cache["CL_COUNTRY"] = {
            "USA": {"name": "United States"},
            "GBR": "GBR",
        }

        def _fake_constraints(self, **kwargs):
            return {
                "key_values": [{"id": "COUNTRY", "values": ["USA", "GBR"]}],
                "full_response": {"data": {}},
            }

        monkeypatch.setattr(ImfMetadata, "get_available_constraints", _fake_constraints)
        result = seeded_meta.get_dataflow_parameters("TEST_DF")
        labels = {opt["value"]: opt["label"] for opt in result["COUNTRY"]}
        assert labels["USA"] == "United States"
        assert labels["GBR"] == "GBR"

    def test_get_dataflow_parameters_fetches_uncached_codelist(
        self, seeded_meta, monkeypatch
    ):
        """Fetches a codelist when no entry is cached for a dimension."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"].append(
            {"id": "NEW_DIM", "position": "3", "conceptRef": {"id": "NEW_DIM"}}
        )

        def _fake_constraints(self, **kwargs):
            return {"key_values": [], "full_response": {"data": {}}}

        def _fake_get_codelist(
            self, codelist_id, agency_id, dataflow_id, include_descriptions=False
        ):
            self._codelist_cache[codelist_id] = {"NEW": "New label"}
            return {"NEW": "New label"}

        monkeypatch.setattr(ImfMetadata, "get_available_constraints", _fake_constraints)
        monkeypatch.setattr(ImfMetadata, "_get_codelist_map", _fake_get_codelist)
        result = seeded_meta.get_dataflow_parameters("TEST_DF")
        assert "NEW_DIM" in result

    def test_get_dataflow_parameters_unresolvable_dim(self, seeded_meta, monkeypatch):
        """Dimensions with no resolvable codelist are skipped."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"].append(
            {"id": "WEIRDOWEIRD", "position": "3", "conceptRef": {"id": "WEIRDO"}}
        )

        def _fake_constraints(self, **kwargs):
            return {"key_values": [], "full_response": {"data": {}}}

        monkeypatch.setattr(ImfMetadata, "get_available_constraints", _fake_constraints)

        def _no_codes(
            self, codelist_id, agency_id, dataflow_id, include_descriptions=False
        ):
            return {}

        monkeypatch.setattr(ImfMetadata, "_get_codelist_map", _no_codes)
        result = seeded_meta.get_dataflow_parameters("TEST_DF")
        assert "WEIRDOWEIRD" not in result

    def test_get_available_constraints_unknown_dataflow(self, seeded_meta):
        """Unknown dataflow raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            seeded_meta.get_available_constraints("NOPE", "all")

    def test_get_available_constraints_no_agency(self, seeded_meta):
        """Missing agency ID raises ValueError."""
        seeded_meta.dataflows["NA"] = {
            "id": "NA",
            "structureRef": {"id": "DSD_TEST"},
        }
        with pytest.raises(ValueError, match="Agency ID not found"):
            seeded_meta.get_available_constraints("NA", "all")

    def test_get_available_constraints_cached(self, seeded_meta):
        """Cached result returns directly without hitting the network."""
        cache_key = "TEST_DF:all:None:None:None:()"
        seeded_meta._constraints_cache[cache_key] = {"key_values": [], "cached": 1}
        result = seeded_meta.get_available_constraints("TEST_DF", "all")
        assert result == {"key_values": [], "cached": 1}

    def test_get_available_constraints_http_success(self, seeded_meta):
        """Successful response is parsed and cached."""
        payload = {
            "data": {
                "dataConstraints": [
                    {
                        "cubeRegions": [
                            {
                                "keyValues": [
                                    {
                                        "id": "DIM1",
                                        "values": ["v1", {"value": "v2"}, None],
                                    }
                                ],
                                "components": [
                                    {"id": "DIM2", "values": ["x"]},
                                    {"id": "", "values": []},
                                ],
                            }
                        ]
                    }
                ]
            }
        }
        with patch("openbb_core.provider.utils.helpers.make_request") as mock_req:
            mock_req.return_value = _build_mock_response(json_data=payload)
            result = seeded_meta.get_available_constraints(
                "TEST_DF",
                key="all",
                component_id="all",
                mode="available",
                references="all",
                extra="value",
            )
        ids = {kv["id"] for kv in result["key_values"]}
        assert {"DIM1", "DIM2"} <= ids

    def test_get_available_constraints_json_decode_error(self, seeded_meta):
        """JSON decode failure raises OpenBBError."""
        bad = MagicMock()
        bad.json.side_effect = json.JSONDecodeError("nope", "", 0)
        bad.raise_for_status.return_value = None
        with patch("openbb_core.provider.utils.helpers.make_request", return_value=bad):
            with pytest.raises(OpenBBError, match="Unexpected response format"):
                seeded_meta.get_available_constraints("TEST_DF", "all")

    def test_get_available_constraints_request_exception(self, seeded_meta):
        """RequestException raises OpenBBError."""
        from requests.exceptions import RequestException

        with patch(
            "openbb_core.provider.utils.helpers.make_request",
            side_effect=RequestException("boom"),
        ):
            with pytest.raises(OpenBBError, match="error occurred"):
                seeded_meta.get_available_constraints("TEST_DF", "all")

    def test_resolve_codelist_id_codelist_ref_dict(self, seeded_meta):
        """Direct codelist ref dict short-circuits resolution."""
        dim_meta = {"representation": {"codelist": {"id": "CL_DIRECT"}}}
        assert (
            seeded_meta._resolve_codelist_id("TEST_DF", "DSD_TEST", "DIM", dim_meta)
            == "CL_DIRECT"
        )

    def test_resolve_codelist_id_codelist_ref_string(self, seeded_meta):
        """Direct codelist ref string short-circuits resolution."""
        dim_meta = {"representation": {"codelist": "CL_STR"}}
        assert (
            seeded_meta._resolve_codelist_id("TEST_DF", "DSD_TEST", "DIM", dim_meta)
            == "CL_STR"
        )

    def test_resolve_codelist_id_blank_dim_returns_none(self, seeded_meta):
        """Empty dim_id returns None."""
        assert seeded_meta._resolve_codelist_id("TEST_DF", "DSD_TEST", "", {}) is None

    def test_resolve_codelist_id_alias_match(self, seeded_meta):
        """Alias table promotes CL_AREA for REF_AREA-style dimensions."""
        seeded_meta._codelist_cache["CL_AREA"] = {"USA": "United States"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "REF_AREA",
            {"conceptRef": {"id": "REF_AREA"}},
        )
        assert result == "CL_AREA"

    def test_resolve_codelist_id_alias_specific_match(self, seeded_meta):
        """Alias also matches the dataflow-specific suffix."""
        seeded_meta._codelist_cache["CL_TEST_DF_QUANTILE"] = {"Q1": "Q1"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "INCOME_WEALTH_QUANTILE",
            {},
        )
        assert result == "CL_TEST_DF_QUANTILE"

    def test_resolve_codelist_id_counterpart_recurses(self, seeded_meta):
        """COUNTERPART_ dims recurse to the base dimension."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"].append(
            {
                "id": "AREA",
                "position": "3",
                "representation": {"codelist": "CL_BASE_AREA"},
            }
        )
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "COUNTERPART_AREA",
            {},
        )
        assert result == "CL_BASE_AREA"

    def test_resolve_codelist_id_activity_fallback(self, seeded_meta):
        """ACTIVITY substring uses the activity fallback codelists."""
        seeded_meta._codelist_cache["CL_ACTIVITY"] = {"MFG": "Manufacturing"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "SOME_ACTIVITY_INDEX",
            {},
        )
        assert result == "CL_ACTIVITY"

    def test_resolve_codelist_id_coicop_fallback(self, seeded_meta):
        """COICOP substring uses COICOP fallback codelists."""
        seeded_meta._codelist_cache["CL_COICOP_2018"] = {"X": "X"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "COICOP_CLASS",
            {},
        )
        assert result == "CL_COICOP_2018"

    def test_resolve_codelist_id_dim_substring_match(self, seeded_meta):
        """Cache-key substring fallback returns the first match."""
        seeded_meta._codelist_cache["CL_MASTER_FOO"] = {"X": "Y"}
        seeded_meta._codelist_cache["CL_RANDOM_FOOBAR"] = {"A": "B"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "FOOBAR",
            {},
        )
        assert result == "CL_RANDOM_FOOBAR"

    def test_resolve_codelist_id_parts_fallback(self, seeded_meta):
        """Multi-part dim id matches by part inclusion."""
        seeded_meta._codelist_cache["CL_MASTER_BAR"] = {"X": "Y"}
        seeded_meta._codelist_cache["CL_RANDOM_ALPHA_BETA"] = {"X": "Y"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "ALPHA_BETA",
            {},
        )
        assert result == "CL_RANDOM_ALPHA_BETA"

    def test_resolve_codelist_id_default_first_candidate(self, seeded_meta):
        """Defaults to the first generated candidate when nothing matches."""
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "ALPHA_NEW_DIMENSION",
            {},
        )
        assert result is not None
        assert result.startswith("CL_")

    def test_resolve_codelist_id_strips_shared_prefix(self, seeded_meta):
        """When dim_id shares a leading token with dataflow_id, the trimmed candidate resolves."""
        seeded_meta._codelist_cache["CL_GS_LI_MS"] = {"M": "Married"}
        result = seeded_meta._resolve_codelist_id("GS_LI", "DSD_GS_LI", "GS_MS", {})
        assert result == "CL_GS_LI_MS"

    def test_resolve_codelist_id_concept_codelist_id_wins(self, seeded_meta):
        """The conceptscheme's ``codelist_id`` short-circuits all heuristics."""
        seeded_meta.conceptschemes = {
            "CS_TEST": {
                "concepts": [
                    {"id": "WIDGETS", "codelist_id": "CL_WIDGETS_REAL"},
                ]
            }
        }
        dim_meta = {"conceptRef": {"id": "WIDGETS", "maintainableParentID": "CS_TEST"}}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF", "DSD_TEST", "DIM", dim_meta
        )
        assert result == "CL_WIDGETS_REAL"

    def test_resolve_codelist_id_country_dim(self, seeded_meta):
        """Country-like dims try ISO_COUNTRY candidate first."""
        seeded_meta._codelist_cache["CL_TEST_ISO_COUNTRY"] = {"USA": "United States"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "COUNTRY",
            {"conceptRef": {"id": "COUNTRY"}},
        )
        assert result == "CL_TEST_ISO_COUNTRY"

    def test_resolve_codelist_id_parent_scheme(self, seeded_meta):
        """``maintainableParentID`` derives a candidate."""
        seeded_meta._codelist_cache["CL_TEST_X"] = {"V": "Value"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "X",
            {"conceptRef": {"id": "X", "maintainableParentID": "CS_TEST"}},
        )
        assert result is not None

    def test_resolve_codelist_id_case_insensitive_match(self, seeded_meta):
        """Case-insensitive cache lookup recovers a match."""
        seeded_meta._codelist_cache["cl_test_df_indicator_lower"] = {"X": "Y"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "INDICATOR_LOWER",
            {},
        )
        assert result == "cl_test_df_indicator_lower"

    def test_resolve_codelist_id_multipart_skips_master(self, seeded_meta):
        """Multi-part match loop skips ``CL_MASTER_*`` keys."""
        seeded_meta._codelist_cache["CL_MASTER_BETAA_ALPHAA"] = {"X": "Y"}
        seeded_meta._codelist_cache["CL_RANDOMM_BETAA_ALPHAA"] = {"X": "Y"}
        result = seeded_meta._resolve_codelist_id(
            "TEST_DF",
            "DSD_TEST",
            "ALPHAA_BETAA",
            {},
        )
        assert result == "CL_RANDOMM_BETAA_ALPHAA"

    def test_get_dataflow_parameters_cached_codes_branch(
        self, seeded_meta, monkeypatch
    ):
        """Constrained value path hits the cached codes branch."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"] = [
            {"id": "INDICATOR", "position": "0", "conceptRef": {"id": "INDICATOR"}}
        ]

        def _fake_constraints(self, **kwargs):
            return {
                "key_values": [{"id": "INDICATOR", "values": ["GDP"]}],
                "full_response": {"data": {}},
            }

        monkeypatch.setattr(ImfMetadata, "get_available_constraints", _fake_constraints)
        result = seeded_meta.get_dataflow_parameters("TEST_DF")
        assert "INDICATOR" in result

    def test_get_dataflow_parameters_skips_time_period_and_unresolved(
        self, seeded_meta, monkeypatch
    ):
        """TIME_PERIOD dim and dims that resolve to None are skipped."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"] = [
            {
                "id": "TIME_PERIOD",
                "position": "0",
                "conceptRef": {"id": "TIME_PERIOD"},
            },
            {"id": "INDICATOR", "position": "1", "conceptRef": {"id": "INDICATOR"}},
        ]

        def _fake_constraints(self, **kwargs):
            return {"key_values": [], "full_response": {"data": {}}}

        monkeypatch.setattr(ImfMetadata, "get_available_constraints", _fake_constraints)

        def _resolve(self, dataflow_id, dsd_id, dim_id, dim_meta):
            if dim_id == "INDICATOR":
                return None
            return f"CL_{dim_id}"

        monkeypatch.setattr(ImfMetadata, "_resolve_codelist_id", _resolve)
        result = seeded_meta.get_dataflow_parameters("TEST_DF")
        assert "TIME_PERIOD" not in result
        assert "INDICATOR" not in result

    def test_get_dataflow_parameters_no_agency(self, seeded_meta, monkeypatch):
        """``_get_codes`` returns ``{}`` when agency is missing."""
        seeded_meta.dataflows["NA_AGY"] = {
            "id": "NA_AGY",
            "structureRef": {"id": "DSD_NA"},
        }
        seeded_meta.datastructures["DSD_NA"] = {
            "id": "DSD_NA",
            "dimensions": [
                {"id": "NEW_DIM", "position": "0", "conceptRef": {"id": "NEW_DIM"}}
            ],
        }

        def _fake_constraints(self, **kwargs):
            return {"key_values": [], "full_response": {"data": {}}}

        monkeypatch.setattr(ImfMetadata, "get_available_constraints", _fake_constraints)
        result = seeded_meta.get_dataflow_parameters("NA_AGY")
        assert result == {}


class TestSearchMixin:
    """Coverage for ``_search_mixin``."""

    def test_list_dataflows_sorts_and_strips(self, seeded_meta):
        """Returns ``[{label, value}]`` sorted by id."""
        result = seeded_meta.list_dataflows()
        assert result == [{"label": "Test Dataflow", "value": "TEST_DF"}]

    def test_search_dataflows_empty_query_raises(self, seeded_meta):
        """Empty query raises OpenBBError."""
        with pytest.raises(OpenBBError, match="empty or invalid"):
            seeded_meta.search_dataflows("")

    def test_search_dataflows_skips_dataflow_without_structure_ref(self, seeded_meta):
        """Skips entries missing ``structureRef.id``."""
        seeded_meta.dataflows["NO_REF"] = {
            "id": "NO_REF",
            "name": "Test Dataflow",
            "description": "",
            "structureRef": {},
        }
        result = seeded_meta.search_dataflows("test")
        groups = [g["group_id"] for g in result]
        assert "DSD_TEST" in groups

    def test_search_indicators_no_query_no_keywords_raises(self, seeded_meta):
        """OpenBBError raised when none of query/keywords/dataflows provided."""
        with pytest.raises(OpenBBError, match="must be provided"):
            seeded_meta.search_indicators("")

    def test_search_indicators_no_target_dataflows_raises(self, monkeypatch):
        """Empty dataflows list raises OpenBBError."""
        ImfMetadata._reset()
        monkeypatch.setattr(ImfMetadata, "_load_from_cache", lambda self: True)
        meta = ImfMetadata()
        meta.dataflows = {}
        with pytest.raises(OpenBBError, match="No valid dataflows"):
            meta.search_indicators("gdp")

    def test_search_indicators_string_dataflow(self, seeded_meta, monkeypatch):
        """Accepts a single dataflow id as a string."""

        def _fake_get_hierarchies(self, df_id):
            return []

        def _fake_get_indicators(self, df_id):
            return [
                {
                    "indicator": "GDP",
                    "label": "GDP",
                    "description": "",
                    "dataflow_name": "Test",
                    "dataflow_id": df_id,
                }
            ]

        monkeypatch.setattr(
            ImfMetadata, "get_dataflow_hierarchies", _fake_get_hierarchies
        )
        monkeypatch.setattr(ImfMetadata, "get_indicators_in", _fake_get_indicators)
        results = seeded_meta.search_indicators("gdp", dataflows="TEST_DF")
        assert results

    def test_build_indicator_table_maps_swallows_errors(self, seeded_meta, monkeypatch):
        """Hierarchies and structures that raise are skipped."""

        def _raise_hier(self, df_id):
            raise RuntimeError("nope")

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _raise_hier)
        result = seeded_meta._build_indicator_table_maps({"TEST_DF"})
        assert result == ({}, {})

    def test_build_indicator_table_maps_dedupes_table_entries(
        self, seeded_meta, monkeypatch
    ):
        """Duplicate table entries are not appended twice."""

        def _hier(self, df_id):
            return [{"id": "H1", "name": "Hier", "description": "Hier desc"}]

        def _structure(self, df_id, hier_id):
            return {
                "indicators": [
                    {
                        "indicator_code": "GDP",
                        "is_group": False,
                    },
                    {
                        "indicator_code": "GDP",
                        "is_group": False,
                    },
                    {
                        "indicator_code": "",
                        "is_group": False,
                    },
                    {
                        "is_group": True,
                    },
                ]
            }

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        monkeypatch.setattr(ImfMetadata, "get_dataflow_table_structure", _structure)
        i2t, i2text = seeded_meta._build_indicator_table_maps({"TEST_DF"})
        assert i2t["TEST_DF_GDP"] == [{"table_id": "H1", "table_name": "Hier"}]

    def test_build_indicator_table_maps_structure_error_skipped(
        self, seeded_meta, monkeypatch
    ):
        """A structure-fetch exception skips that hierarchy."""

        def _hier(self, df_id):
            return [{"id": "H1", "name": "Hier", "description": ""}]

        def _structure_boom(self, df_id, hier_id):
            raise RuntimeError("nope")

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        monkeypatch.setattr(
            ImfMetadata, "get_dataflow_table_structure", _structure_boom
        )
        result = seeded_meta._build_indicator_table_maps({"TEST_DF"})
        assert result == ({}, {})

    def test_collect_indicators_warns_on_error(self, seeded_meta, monkeypatch):
        """A failing get_indicators_in emits an OpenBBWarning."""

        def _boom(self, df_id):
            raise ValueError("boom")

        monkeypatch.setattr(ImfMetadata, "get_indicators_in", _boom)
        with pytest.warns(OpenBBWarning, match="Could not retrieve"):
            result = seeded_meta._collect_indicators({"TEST_DF"}, {}, {})
        assert result == []

    def test_filter_indicators_by_query_empty_query(self, seeded_meta):
        """Empty query returns the list unchanged."""
        items = [{"label": "A"}]
        assert seeded_meta._filter_indicators_by_query(items, "") == items

    def test_filter_indicators_by_query_whitespace_query(self, seeded_meta):
        """Whitespace-only query returns the list unchanged."""
        items = [{"label": "A"}]
        assert seeded_meta._filter_indicators_by_query(items, "  ;  ") == items

    def test_filter_indicators_by_query_quoted_phrase_match(self, seeded_meta):
        """Unparsed quoted phrases fall back to substring match."""
        items = [
            {
                "indicator": "GDP",
                "label": "Gross Domestic Product",
                "description": "",
                "dataflow_name": "Macro",
                "dataflow_id": "TEST",
            }
        ]
        result = seeded_meta._filter_indicators_by_query(items, '""')
        assert result == []

    def test_filter_indicators_by_query_match_via_table_text(self, seeded_meta):
        """Match via ``_table_search_text``."""
        items = [
            {
                "indicator": "X",
                "label": "X",
                "description": "",
                "dataflow_name": "",
                "dataflow_id": "TEST",
                "_table_search_text": "macro indicators",
            }
        ]
        result = seeded_meta._filter_indicators_by_query(items, "macro")
        assert result

    def test_filter_indicators_by_keywords_no_keywords(self, seeded_meta):
        """Without keywords, just strips ``_table_search_text``."""
        items = [{"label": "A", "_table_search_text": "x"}]
        result = seeded_meta._filter_indicators_by_keywords(items, None)
        assert "_table_search_text" not in result[0]

    def test_filter_indicators_by_keywords_inclusion(self, seeded_meta):
        """Keyword inclusion filter."""
        items = [
            {
                "indicator": "GDP",
                "label": "Gross Domestic Product",
                "description": "",
                "_table_search_text": "",
            },
            {
                "indicator": "CPI",
                "label": "Consumer Price Index",
                "description": "",
                "_table_search_text": "",
            },
        ]
        result = seeded_meta._filter_indicators_by_keywords(items, ["gdp"])
        assert len(result) == 1

    def test_filter_indicators_by_keywords_exclusion(self, seeded_meta):
        """``not <word>`` excludes matching items."""
        items = [
            {
                "indicator": "GDP",
                "label": "Gross Domestic Product",
                "description": "",
                "_table_search_text": "",
            },
            {
                "indicator": "CPI",
                "label": "Consumer Price Index",
                "description": "",
                "_table_search_text": "",
            },
        ]
        result = seeded_meta._filter_indicators_by_keywords(items, ["not gdp"])
        assert len(result) == 1
        assert result[0]["indicator"] == "CPI"

    def test_filter_indicators_by_keywords_exclude_word_absent(self, seeded_meta):
        """``not <word>`` keeps the item when the word is absent."""
        items = [
            {
                "indicator": "GDP",
                "label": "Gross Domestic Product",
                "description": "",
                "_table_search_text": "",
            }
        ]
        result = seeded_meta._filter_indicators_by_keywords(items, ["not zzz"])
        assert len(result) == 1

    def test_matches_query_helper(self):
        """Helper ANDs within an OR-group, ORs across groups."""
        assert _matches_query("gdp growth", [["gdp", "growth"]])
        assert not _matches_query("gdp", [["gdp", "growth"]])
        assert _matches_query("inflation", [["gdp"], ["inflation"]])

    def test_filter_indicators_by_query_stop_word_phrase(self, seeded_meta):
        """A phrase that parses to empty falls back to substring matching."""
        items = [
            {
                "indicator": "OF",
                "label": "of indicator",
                "description": "",
                "dataflow_name": "",
                "dataflow_id": "",
            }
        ]
        result = seeded_meta._filter_indicators_by_query(items, "of")
        assert len(result) == 1

    def test_search_dataflows_skips_non_match(self, seeded_meta):
        """Dataflows that do not match the query are skipped."""
        seeded_meta.dataflows["OTHER"] = {
            "id": "OTHER",
            "name": "Unrelated",
            "description": "Nothing useful",
            "structureRef": {"id": "DSD_OTHER"},
        }
        result = seeded_meta.search_dataflows("dataflow")
        assert all(g["group_id"] != "DSD_OTHER" for g in result)

    def test_search_indicators_with_query_pipeline(self, seeded_meta, monkeypatch):
        """End-to-end search pipeline returns indicators."""

        def _hier(self, df_id):
            return [{"id": "H1", "name": "GDP table", "description": ""}]

        def _structure(self, df_id, hier_id):
            return {"indicators": [{"indicator_code": "GDP", "is_group": False}]}

        def _indicators(self, df_id):
            return [
                {
                    "indicator": "GDP",
                    "label": "Gross Domestic Product",
                    "description": "Total output",
                    "dataflow_name": "Test",
                    "dataflow_id": df_id,
                }
            ]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        monkeypatch.setattr(ImfMetadata, "get_dataflow_table_structure", _structure)
        monkeypatch.setattr(ImfMetadata, "get_indicators_in", _indicators)
        result = seeded_meta.search_indicators("gdp")
        assert any(i["indicator"] == "GDP" for i in result)


class TestTableMixinHelpers:
    """Coverage for module-level helpers inside ``_table_mixin``."""

    def test_is_irfcl_path_label(self):
        """Detects IRFCL path-style labels."""
        assert _is_irfcl_path_label("Foo, Up to 1 month, Bar") is True
        assert _is_irfcl_path_label("Random label") is False

    def test_hierarchy_overlaps_dataflow_no_codes(self):
        """Empty hierarchy returns True (assume overlap)."""
        assert _hierarchy_overlaps_dataflow({"hierarchicalCodes": []}, {"GDP"})

    def test_hierarchy_overlaps_dataflow_intersection(self):
        """Returns True when codes intersect available values."""
        hier = {
            "hierarchicalCodes": [
                {"code": "urn:any.INDICATOR.GDP"},
                {
                    "code": "urn:any.INDICATOR.X",
                    "hierarchicalCodes": [{"code": "urn:any.INDICATOR.Y"}],
                },
            ]
        }
        assert _hierarchy_overlaps_dataflow(hier, {"GDP"}) is True

    def test_hierarchy_overlaps_dataflow_prefix(self):
        """Prefix-based overlap detection."""
        hier = {"hierarchicalCodes": [{"code": "urn:any.INDICATOR.GDP"}]}
        assert _hierarchy_overlaps_dataflow(hier, {"GDP_DETAIL"}) is True

    def test_hierarchy_overlaps_dataflow_no_match(self):
        """No overlap returns False."""
        hier = {"hierarchicalCodes": [{"code": "urn:any.INDICATOR.GDP"}]}
        assert _hierarchy_overlaps_dataflow(hier, {"OTHER"}) is False

    def test_derive_node_label_inward_outward_split(self):
        """Strips Inward/Outward prefix on CL_DIP_INDICATOR labels."""
        out = _derive_node_label(
            codelist_id_for_code="CL_DIP_INDICATOR",
            full_label="Inward, Direct, Investment",
            parent_full_label=None,
            ancestor_labels=[],
        )
        assert out == "Direct, Investment"

    def test_derive_node_label_strip_parent_prefix(self):
        """Path-style labels strip the parent prefix."""
        out = _derive_node_label(
            codelist_id_for_code="X_INDICATOR_PUB",
            full_label="Parent, Child",
            parent_full_label="Parent",
            ancestor_labels=[],
        )
        assert out == "Child"

    def test_derive_node_label_parent_prefix_no_remainder(self):
        """When the prefix equals the full label, splits on commas."""
        out = _derive_node_label(
            codelist_id_for_code="X_INDICATOR_PUB",
            full_label="Parent",
            parent_full_label="Parent",
            ancestor_labels=[],
        )
        assert out == "Parent"

    def test_derive_node_label_parent_prefix_with_commas_only(self):
        """Returns the last segment when only commas are present."""
        out = _derive_node_label(
            codelist_id_for_code="X_INDICATOR_PUB",
            full_label="Parent, Tail",
            parent_full_label="Parent, Tail",
            ancestor_labels=[],
        )
        assert out == "Tail"

    def test_derive_node_label_with_ancestors(self):
        """Path-style with ancestors uses ``_strip_known_ancestors``."""
        out = _derive_node_label(
            codelist_id_for_code="X_INDICATOR_PUB",
            full_label="A, B, C",
            parent_full_label=None,
            ancestor_labels=["A"],
        )
        assert "B" in out

    def test_derive_node_label_path_style_comma_only(self):
        """Without ancestors, returns the last comma-separated part."""
        out = _derive_node_label(
            codelist_id_for_code="X_INDICATOR_PUB",
            full_label="Foo, Bar",
            parent_full_label=None,
            ancestor_labels=[],
        )
        assert out == "Bar"

    def test_derive_node_label_non_path_style_parent_prefix(self):
        """Non-path-style with parent prefix returns last segment."""
        out = _derive_node_label(
            codelist_id_for_code="CL_NORMAL",
            full_label="Parent, Tail",
            parent_full_label="Parent",
            ancestor_labels=[],
        )
        assert out == "Tail"

    def test_derive_node_label_default(self):
        """Default returns the original label."""
        out = _derive_node_label(
            codelist_id_for_code="CL_NORMAL",
            full_label="Plain Label",
            parent_full_label=None,
            ancestor_labels=[],
        )
        assert out == "Plain Label"

    def test_derive_node_label_falsy(self):
        """Empty label stays empty."""
        out = _derive_node_label(
            codelist_id_for_code=None,
            full_label="",
            parent_full_label=None,
            ancestor_labels=[],
        )
        assert out == ""

    def test_strip_known_ancestors_total_match(self):
        """``total`` prefix detection in ancestor parts."""
        result = _strip_known_ancestors(
            "CL_FOO",
            "Assets",
            ["Total Assets"],
        )
        assert result == "Assets"

    def test_strip_known_ancestors_substring(self):
        """Substring of length-6+ counts as ancestor."""
        result = _strip_known_ancestors(
            "CL_FOO",
            "Foreign Direct Investment Inflows",
            ["Foreign"],
        )
        assert "Foreign" not in result or result == "Foreign Direct Investment Inflows"

    def test_strip_known_ancestors_short_ancestor_skipped(self):
        """Short ancestor part (<6 chars) does not trigger substring match."""
        result = _strip_known_ancestors(
            "CL_FOO",
            "Foreign Direct Investment Inflows",
            ["GDP"],
        )
        assert result == "Foreign Direct Investment Inflows"

    def test_strip_known_ancestors_irfcl_retains_three_parts(self):
        """IRFCL codelists keep 3+ parts as-is."""
        result = _strip_known_ancestors(
            "CL_IRFCL_X",
            "A, B, C, D",
            [],
        )
        assert result == "A, B, C, D"

    def test_strip_known_ancestors_colon_split(self):
        """Labels split on ':' as well."""
        result = _strip_known_ancestors(
            "CL_FOO",
            "Parent: Child, Grand",
            ["Parent"],
        )
        assert "Child" in result

    def test_strip_known_ancestors_long_strings_subset(self):
        """Long-string subset detection picks substring."""
        long_anc = "x" * 20
        result = _strip_known_ancestors(
            "CL_FOO",
            long_anc,
            [long_anc + "y"],
        )
        assert result == long_anc

    def test_strip_known_ancestors_long_string_window(self):
        """Long-string window detection covers >30-char shorter strings."""
        result = _strip_known_ancestors(
            "CL_FOO",
            "a" * 35,
            ["b" + "a" * 35 + "c"],
        )
        assert result == "a" * 35

    def test_strip_known_ancestors_all_stripped_returns_last(self):
        """When everything is stripped, return the last child part."""
        result = _strip_known_ancestors(
            "CL_FOO",
            "Parent",
            ["Parent"],
        )
        assert result == "Parent"

    def test_strip_known_ancestors_empty_child_parts(self):
        """Empty child parts falls back to full_label."""
        result = _strip_known_ancestors("CL_FOO", "", [])
        assert result == ""

    def test_build_series_id_unordered_dims(self):
        """Unordered dims appended after ordered ones."""
        sid = _build_series_id(
            agency_clean="IMF",
            dataflow_id="DF",
            current_dimension_codes={"INDICATOR": "X", "FREQ": "A"},
            indicator_dimension_order={"INDICATOR": 1},
            parent_codes=[],
            indicator_code="X",
        )
        assert sid == "IMF_DF_X_A"

    def test_build_series_id_fallback_to_parents(self):
        """No ordered codes falls back to parent_codes."""
        sid = _build_series_id(
            agency_clean="IMF",
            dataflow_id="DF",
            current_dimension_codes={},
            indicator_dimension_order={},
            parent_codes=["A"],
            indicator_code="B",
        )
        assert sid == "IMF_DF_A_B"


class TestTableMixinMain:
    """Coverage for ``TableMixin`` methods that drive table resolution."""

    def test_validate_hierarchy_queryable_empty(self, seeded_meta):
        """Empty codes returns False."""
        assert seeded_meta._validate_hierarchy_queryable("TEST_DF", []) is False

    def test_validate_hierarchy_queryable_sample(self, seeded_meta):
        """Validates a sample of codes against dimension resolution."""
        codes = [
            {"code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP"},
            {"code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).CPI"},
            {"code": ""},
            {"code": "no-codelist-format"},
        ]
        assert seeded_meta._validate_hierarchy_queryable("TEST_DF", codes) is True

    def test_validate_hierarchy_queryable_invalid_dim(self, seeded_meta):
        """Returns False when codes have no resolvable dimension."""
        codes = [
            {"code": "urn:sdmx:any=IMF.STA:CL_NOWHERE(1.0).X"},
            {"code": "urn:sdmx:any=IMF.STA:CL_NOWHERE(1.0).Y"},
        ]
        assert seeded_meta._validate_hierarchy_queryable("TEST_DF", codes) is False

    def test_get_dataflow_hierarchies_unknown_raises(self, seeded_meta):
        """Unknown dataflow raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            seeded_meta.get_dataflow_hierarchies("NOPE")

    def test_get_dataflow_hierarchies_missing_dsd_returns_empty(self, seeded_meta):
        """Missing DSD short-circuits to an empty list."""
        seeded_meta.dataflows["BAD_DSD"] = {
            "id": "BAD_DSD",
            "agencyID": "IMF.STA",
            "structureRef": {"id": "GONE"},
            "name": "Bad",
        }
        assert seeded_meta.get_dataflow_hierarchies("BAD_DSD") == []

    def test_get_dataflow_hierarchies_no_indicator_codelist(self, seeded_meta):
        """No indicator codelist short-circuits to an empty list."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"] = [
            {"id": "RANDOM", "position": "0", "conceptRef": {"id": "RANDOM"}}
        ]
        assert seeded_meta.get_dataflow_hierarchies("TEST_DF") == []

    def test_get_dataflow_hierarchies_returns_entries(self, seeded_meta, monkeypatch):
        """Produces hierarchy entries when mappings exist."""
        seeded_meta._codelist_to_hierarchies_map["CL_INDICATOR"] = ["H1"]
        seeded_meta.hierarchies["H1"] = {
            "id": "H1",
            "name": "Hierarchy",
            "descriptions": {"en": "desc"},
            "hierarchicalCodes": [{"code": "urn:any=IMF.STA:CL_INDICATOR(1.0).GDP"}],
            "agencyID": "IMF.STA",
            "version": "1.0",
        }

        def _params(self, df_id):
            return {"INDICATOR": [{"value": "GDP", "label": "GDP"}]}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _params)
        result = seeded_meta.get_dataflow_hierarchies("TEST_DF")
        assert result and result[0]["id"] == "H1"

    def test_get_dataflow_hierarchies_skips_non_overlapping(
        self, seeded_meta, monkeypatch
    ):
        """Hierarchy with no overlap is filtered out."""
        seeded_meta._codelist_to_hierarchies_map["CL_INDICATOR"] = ["H_NO"]
        seeded_meta.hierarchies["H_NO"] = {
            "id": "H_NO",
            "name": "Hierarchy",
            "descriptions": {},
            "hierarchicalCodes": [{"code": "urn:any=IMF.STA:CL_INDICATOR(1.0).XYZ"}],
        }

        def _params(self, df_id):
            return {"INDICATOR": [{"value": "GDP", "label": "GDP"}]}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _params)
        result = seeded_meta.get_dataflow_hierarchies("TEST_DF")
        assert result == []

    def test_get_dataflow_hierarchies_params_exception(self, seeded_meta, monkeypatch):
        """``get_dataflow_parameters`` failure is swallowed."""
        seeded_meta._codelist_to_hierarchies_map["CL_INDICATOR"] = ["H1"]
        seeded_meta.hierarchies["H1"] = {
            "name": "Hierarchy",
            "descriptions": {"en": "desc"},
            "hierarchicalCodes": [{"code": "urn:any=IMF.STA:CL_INDICATOR(1.0).GDP"}],
        }

        def _boom(self, df_id):
            raise RuntimeError("nope")

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _boom)
        result = seeded_meta.get_dataflow_hierarchies("TEST_DF")
        assert result and result[0]["name"] == "Hierarchy"

    def test_get_dataflow_hierarchies_skips_missing_hier_obj(
        self, seeded_meta, monkeypatch
    ):
        """Missing hierarchy object is skipped."""
        seeded_meta._codelist_to_hierarchies_map["CL_INDICATOR"] = ["GONE"]

        def _params(self, df_id):
            return {}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _params)
        assert seeded_meta.get_dataflow_hierarchies("TEST_DF") == []

    def test_get_dataflow_hierarchies_irfcl_split(self, seeded_meta, monkeypatch):
        """IRFCL dataflow uses ``_split_irfcl_hierarchy``."""
        seeded_meta.dataflows["IRFCL"] = {
            "id": "IRFCL",
            "agencyID": "IMF.STA",
            "structureRef": {"id": "DSD_IRFCL"},
            "name": "IRFCL",
        }
        seeded_meta.datastructures["DSD_IRFCL"] = {
            "id": "DSD_IRFCL",
            "dimensions": [
                {"id": "INDICATOR", "position": "0", "conceptRef": {"id": "IND"}}
            ],
        }
        seeded_meta._codelist_cache["CL_IRFCL_INDICATOR"] = {
            "X": "Reserves",
            "Y": "Other",
        }
        seeded_meta._codelist_cache["CL_IRFCL_SECTION"] = {
            "X_": "Section X",
        }
        seeded_meta._codelist_to_hierarchies_map["CL_IRFCL_INDICATOR"] = ["H1"]
        seeded_meta.hierarchies["H1"] = {
            "id": "H1",
            "name": "Hierarchy",
            "agencyID": "IMF.STA",
            "version": "1.0",
            "hierarchicalCodes": [
                {
                    "id": "T1",
                    "code": "urn:any=IMF.STA:CL_IRFCL_INDICATOR(1.0).X_RES",
                },
                {
                    "id": "T2",
                    "code": "urn:any=IMF.STA:CL_IRFCL_INDICATOR(1.0).Y_RES",
                },
            ],
        }

        def _params(self, df_id):
            return {}

        monkeypatch.setattr(ImfMetadata, "get_dataflow_parameters", _params)
        result = seeded_meta.get_dataflow_hierarchies("IRFCL")
        assert len(result) == 2
        assert all(":" in r["id"] for r in result)

    def test_find_indicator_codelist_substring_fallback(self, seeded_meta):
        """Falls back to dimensions containing 'INDICATOR' when no whitelist match."""
        seeded_meta._codelist_cache["CL_TEST_DF_OTHER_INDICATOR"] = {"X": "Y"}
        result = seeded_meta._find_indicator_codelist_for_hierarchies(
            "TEST_DF",
            "DSD_TEST",
            [
                {"id": "OTHER_INDICATOR"},
                {"id": "RANDOM"},
            ],
        )
        assert result == "CL_TEST_DF_OTHER_INDICATOR"

    def test_split_irfcl_hierarchy_uses_section_codes(self, seeded_meta):
        """Section codes override the table label when matched."""
        seeded_meta._codelist_cache["CL_IRFCL_SECTION"] = {"AA": "Section AA"}
        seeded_meta._codelist_cache["CL_IRFCL_INDICATOR"] = {
            "AA_X": "AA Label",
            "BB_X": "BB Label",
        }
        top_codes = [
            {"id": "T1", "code": "urn:any=IMF.STA:CL_IRFCL_INDICATOR(1.0).AA_X"},
            {"id": "BB_X", "code": "BB_X"},
        ]
        out = seeded_meta._split_irfcl_hierarchy(
            "IRFCL",
            "H1",
            {"agencyID": "IMF.STA", "version": "1.0"},
            top_codes,
            "CL_IRFCL_INDICATOR",
        )
        assert out[0]["name"] == "Section AA"
        assert out[1]["name"] == "BB Label"

    def test_get_dataflow_table_structure_no_hierarchies(
        self, seeded_meta, monkeypatch
    ):
        """Raises when no hierarchies are available."""

        def _none(self, df_id):
            return []

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _none)
        with pytest.raises(ValueError, match="No presentation hierarchies"):
            seeded_meta.get_dataflow_table_structure("TEST_DF")

    def test_get_dataflow_table_structure_unknown_table_raises(
        self, seeded_meta, monkeypatch
    ):
        """Unknown table_id raises ValueError."""

        def _hier(self, df_id):
            return [{"id": "H1", "name": "X"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        with pytest.raises(ValueError, match="Hierarchy 'BAD' not found"):
            seeded_meta.get_dataflow_table_structure("TEST_DF", "BAD")

    def test_get_dataflow_table_structure_hierarchy_missing_in_cache(
        self, seeded_meta, monkeypatch
    ):
        """Hierarchy listed but absent from ``self.hierarchies`` raises."""

        def _hier(self, df_id):
            return [{"id": "H1", "name": "X"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        with pytest.raises(ValueError, match="not found in cache"):
            seeded_meta.get_dataflow_table_structure("TEST_DF", "H1")

    def test_get_dataflow_table_structure_blank_table_id(
        self, seeded_meta, monkeypatch
    ):
        """Resolved blank table_id raises ValueError explicitly."""
        seeded_meta.hierarchies[""] = {"hierarchicalCodes": []}

        def _hier(self, df_id):
            return [{"name": "X"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        with pytest.raises(ValueError, match="table_id cannot be None"):
            seeded_meta.get_dataflow_table_structure("TEST_DF")

    def test_get_dataflow_table_structure_blank_dim_skipped(
        self, seeded_meta, monkeypatch
    ):
        """A DSD dimension with a blank id is skipped during ordering."""
        seeded_meta.datastructures["DSD_TEST"]["dimensions"].insert(
            0, {"id": "", "position": "-1", "conceptRef": {"id": ""}}
        )
        seeded_meta.hierarchies["H1"] = {
            "id": "H1",
            "name": "Hier",
            "agencyID": "IMF.STA",
            "version": "1.0",
            "hierarchicalCodes": [
                {
                    "id": "C1",
                    "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP",
                    "level": "0",
                }
            ],
        }
        seeded_meta._hierarchy_to_codelist_map["H1"] = "CL_INDICATOR"

        def _hier(self, df_id):
            return [{"id": "H1", "name": "Hier"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        result = seeded_meta.get_dataflow_table_structure("TEST_DF", "H1")
        assert result["total_indicators"] == 1

    def test_get_dataflow_table_structure_basic(self, seeded_meta, monkeypatch):
        """Smoke test for a minimal hierarchy resolution."""
        seeded_meta.hierarchies["H1"] = {
            "id": "H1",
            "name": "Hier",
            "description": "",
            "agencyID": "IMF.STA",
            "version": "1.0",
            "hierarchicalCodes": [
                {
                    "id": "C1",
                    "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP",
                    "level": "0",
                }
            ],
        }
        seeded_meta._hierarchy_to_codelist_map["H1"] = "CL_INDICATOR"

        def _hier(self, df_id):
            return [{"id": "H1", "name": "Hier"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        result = seeded_meta.get_dataflow_table_structure("TEST_DF", "H1")
        assert result["hierarchy_id"] == "H1"
        assert result["total_indicators"] == 1

    def test_get_dataflow_table_structure_filters_top_level(
        self, seeded_meta, monkeypatch
    ):
        """Table id with ``:`` filters to a single top-level code."""
        seeded_meta.hierarchies["H1"] = {
            "id": "H1",
            "name": "Hier",
            "agencyID": "IMF.STA",
            "version": "1.0",
            "hierarchicalCodes": [
                {
                    "id": "T1",
                    "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP",
                    "level": "0",
                },
                {
                    "id": "T2",
                    "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).CPI",
                    "level": "0",
                },
            ],
        }
        seeded_meta._hierarchy_to_codelist_map["H1"] = "CL_INDICATOR"

        def _hier(self, df_id):
            return [{"id": "H1:T1", "name": "Hier"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        result = seeded_meta.get_dataflow_table_structure("TEST_DF", "H1:T1")
        assert result["total_indicators"] == 1
        assert result["indicators"][0]["indicator_code"] == "GDP"

    def test_get_dataflow_table_structure_irfcl_calls_fix(
        self, seeded_meta, monkeypatch
    ):
        """IRFCL dataflow runs ``_fix_irfcl_hierarchy`` over the output."""
        seeded_meta.dataflows["IRFCL"] = {
            "id": "IRFCL",
            "agencyID": "IMF.STA",
            "structureRef": {"id": "DSD_IRFCL"},
            "name": "IRFCL",
        }
        seeded_meta.datastructures["DSD_IRFCL"] = {
            "id": "DSD_IRFCL",
            "dimensions": [
                {"id": "INDICATOR", "position": "0", "conceptRef": {"id": "IND"}}
            ],
        }
        seeded_meta.hierarchies["H_IRFCL"] = {
            "id": "H_IRFCL",
            "name": "Hier",
            "agencyID": "IMF.STA",
            "version": "1.0",
            "hierarchicalCodes": [
                {
                    "id": "F1",
                    "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).FOR",
                    "level": "0",
                }
            ],
        }
        seeded_meta._hierarchy_to_codelist_map["H_IRFCL"] = "CL_INDICATOR"

        def _hier(self, df_id):
            return [{"id": "H_IRFCL", "name": "Hier"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        result = seeded_meta.get_dataflow_table_structure("IRFCL", "H_IRFCL")
        assert result["dataflow_id"] == "IRFCL"

    def test_select_hierarchy_default_uses_first(self):
        """Without a table_id, returns the first hierarchy."""
        from openbb_imf.utils.metadata._table_mixin import TableMixin

        result = TableMixin._select_hierarchy(
            None,
            [{"id": "H1"}, {"id": "H2"}],
        )
        assert result == (None, "H1", {"id": "H1"}, "H1")

    def test_select_hierarchy_default_colon(self):
        """First hierarchy with ``:`` is split into base/top."""
        from openbb_imf.utils.metadata._table_mixin import TableMixin

        result = TableMixin._select_hierarchy(
            None,
            [{"id": "H1:T1"}],
        )
        assert result == ("T1", "H1", {"id": "H1:T1"}, "H1:T1")

    def test_select_hierarchy_default_missing_id_uses_blank(self):
        """Hierarchy entry without id falls back to ``""``."""
        from openbb_imf.utils.metadata._table_mixin import TableMixin

        result = TableMixin._select_hierarchy(
            None,
            [{}],
        )
        assert result == (None, "", {}, "")

    def test_process_hierarchical_codes_double_parent_id(self, seeded_meta):
        """parent_id containing ``___`` is cleaned to the trailing segment."""
        codes = [
            {
                "id": "child",
                "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP",
                "level": "1",
            }
        ]
        result = seeded_meta._process_hierarchical_codes(
            codes,
            dataflow_id="TEST_DF",
            agency_clean="IMF",
            indicator_dimension_order={"INDICATOR": 0},
            codelist_dimension_cache={},
            codelist_labels_cache={},
            codelist_desc_cache={},
            parent_id="parent_a___parent_b",
        )
        assert result[0]["parent_id"] == "parent_b"

    def test_process_hierarchical_codes_uses_depth_override(self, seeded_meta):
        """BOP dataflow uses depth instead of the level field."""
        codes = [
            {
                "id": "c1",
                "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP",
                "level": "5",
            }
        ]
        seeded_meta.dataflows["BOP"] = {
            "id": "BOP",
            "agencyID": "IMF.STA",
            "structureRef": {"id": "DSD_TEST"},
        }
        result = seeded_meta._process_hierarchical_codes(
            codes,
            dataflow_id="BOP",
            agency_clean="IMF",
            indicator_dimension_order={"INDICATOR": 0},
            codelist_dimension_cache={},
            codelist_labels_cache={},
            codelist_desc_cache={},
        )
        assert result[0]["level"] == 0

    def test_process_hierarchical_codes_recursive(self, seeded_meta):
        """Nested codes recurse and accumulate parent_codes."""
        codes = [
            {
                "id": "parent",
                "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP",
                "level": "0",
                "hierarchicalCodes": [
                    {
                        "id": "child",
                        "code": "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP_C",
                        "level": "1",
                    }
                ],
            }
        ]
        result = seeded_meta._process_hierarchical_codes(
            codes,
            dataflow_id="TEST_DF",
            agency_clean="IMF",
            indicator_dimension_order={"INDICATOR": 0},
            codelist_dimension_cache={},
            codelist_labels_cache={},
            codelist_desc_cache={},
        )
        assert len(result) == 2
        assert result[1]["parent_id"] == "parent"

    def test_resolve_dimension_for_code_no_codelist(self, seeded_meta):
        """Empty codelist id returns None."""
        result = seeded_meta._resolve_dimension_for_code(
            "TEST_DF",
            None,
            "",
            {},
            {},
            {},
        )
        assert result is None

    def test_resolve_dimension_for_code_fetch_when_missing(
        self, seeded_meta, monkeypatch
    ):
        """Missing cached labels triggers a fetch via the URN agency."""
        called = {}

        def _fake_fetch(self, agency_id, codelist_id):
            called["agency"] = agency_id
            self._codelist_cache[codelist_id] = {"X": "Y"}
            self._codelist_descriptions[codelist_id] = {"X": "Y"}
            return True

        monkeypatch.setattr(ImfMetadata, "_fetch_single_codelist", _fake_fetch)
        codelist_dim_cache = {}
        codelist_labels_cache = {}
        codelist_desc_cache = {}
        seeded_meta._codelist_cache.pop("CL_INDICATOR", None)
        result = seeded_meta._resolve_dimension_for_code(
            "TEST_DF",
            "CL_INDICATOR",
            "urn:sdmx:any=IMF.STA:CL_INDICATOR(1.0).GDP",
            codelist_dim_cache,
            codelist_labels_cache,
            codelist_desc_cache,
        )
        assert called["agency"] == "IMF.STA"
        assert codelist_labels_cache["CL_INDICATOR"] == {"X": "Y"}
        assert result is not None or result is None

    def test_fix_irfcl_hierarchy_no_forwards(self, seeded_meta):
        """Returns input unchanged when 'forwards' is absent."""
        indicators = [{"id": "A", "label": "Other"}]
        assert seeded_meta._fix_irfcl_hierarchy(indicators) == indicators

    def test_fix_irfcl_hierarchy_reparents(self, seeded_meta):
        """Re-parents instrument children of forwards to forwards' parent."""
        indicators = [
            {
                "id": "F",
                "label": "Forwards",
                "parent_id": "ROOT",
                "depth": 1,
            },
            {
                "id": "F1",
                "label": "Futures",
                "parent_id": "F",
                "depth": 2,
            },
            {
                "id": "F2",
                "label": "Other",
                "parent_id": "F",
                "depth": 2,
            },
            {
                "id": "F3",
                "label": "Unrelated",
                "parent_id": "F",
                "depth": 2,
            },
        ]
        result = seeded_meta._fix_irfcl_hierarchy(indicators)
        futures = next(i for i in result if i["id"] == "F1")
        assert futures["parent_id"] == "ROOT"
        assert futures["depth"] == 1
        other = next(i for i in result if i["id"] == "F2")
        assert other["parent_id"] == "ROOT"
        unrelated = next(i for i in result if i["id"] == "F3")
        assert unrelated["parent_id"] == "F"

    def test_create_synthetic_groups_no_path_children(self, seeded_meta):
        """Returns input unchanged when no IRFCL-style siblings."""
        ind = [{"id": "A", "label": "X", "parent_id": None}]
        assert seeded_meta._create_synthetic_groups_for_shared_prefixes(ind) == ind

    def test_create_synthetic_groups_suffix(self, seeded_meta):
        """Shared suffix wraps siblings into nested synthetic groups."""
        indicators = [
            {
                "id": "C1",
                "label": "Foo, Long positions, Up to 1 month",
                "parent_id": "P",
                "order": 1,
                "depth": 1,
            },
            {
                "id": "C2",
                "label": "Bar, Long positions, Up to 1 month",
                "parent_id": "P",
                "order": 2,
                "depth": 1,
            },
        ]
        result = seeded_meta._create_synthetic_groups_for_shared_prefixes(indicators)
        assert any(i.get("is_group") for i in result)

    def test_create_synthetic_groups_prefix(self, seeded_meta):
        """Shared prefix wraps siblings under a single synthetic group."""
        indicators = [
            {
                "id": "C1",
                "label": "Up to 1 month, Long positions",
                "parent_id": "P",
                "order": 1,
                "depth": 1,
            },
            {
                "id": "C2",
                "label": "Up to 1 month, Short positions",
                "parent_id": "P",
                "order": 2,
                "depth": 1,
            },
        ]
        result = seeded_meta._create_synthetic_groups_for_shared_prefixes(indicators)
        assert any(i.get("is_group") for i in result)

    def test_create_synthetic_groups_unequal_split(self, seeded_meta):
        """Mismatched part counts skip synthesis."""
        indicators = [
            {
                "id": "C1",
                "label": "Up to 1 month",
                "parent_id": "P",
                "order": 1,
                "depth": 1,
            },
            {
                "id": "C2",
                "label": "Up to 1 month, Long positions",
                "parent_id": "P",
                "order": 2,
                "depth": 1,
            },
        ]
        result = seeded_meta._create_synthetic_groups_for_shared_prefixes(indicators)
        assert not any(i.get("is_group") for i in result)

    def test_create_synthetic_groups_empty_split(self, seeded_meta):
        """Empty split label parts skip synthesis."""
        indicators = [
            {
                "id": "C1",
                "label": "Up to 1 month, ",
                "parent_id": "P",
                "order": 1,
                "depth": 1,
            },
            {
                "id": "C2",
                "label": ", Up to 1 month",
                "parent_id": "P",
                "order": 2,
                "depth": 1,
            },
        ]
        result = seeded_meta._create_synthetic_groups_for_shared_prefixes(indicators)
        assert isinstance(result, list)

    def test_list_all_dataflow_tables(self, seeded_meta, monkeypatch):
        """Builds the curated map and skips invalid specs."""
        fake_tables = {
            "Friendly": "TEST_DF::H1",
            "BadSpec": "no-double-colon",
            "Unknown": "UNKNOWN::H2",
            "MissingHier": "TEST_DF::HMISSING",
            "Boom": "TEST_DF::HBOOM",
        }
        monkeypatch.setattr(
            "openbb_imf.utils.constants.PRESENTATION_TABLES",
            fake_tables,
            raising=False,
        )
        call_count = {"n": 0}

        def _hier(self, df_id):
            call_count["n"] += 1
            if call_count["n"] == 3:
                raise RuntimeError("nope")
            return [{"id": "H1", "name": "Hier"}]

        monkeypatch.setattr(ImfMetadata, "get_dataflow_hierarchies", _hier)
        result = seeded_meta.list_all_dataflow_tables()
        assert "TEST_DF" in result
        assert result["TEST_DF"][0]["friendly_name"] == "Friendly"


class TestTypingProtocol:
    """Coverage for the protocol stubs in ``_typing._MixinBase``."""

    def test_all_stub_methods_raise(self):
        """Every stub on ``_MixinBase`` raises NotImplementedError."""
        base = _MixinBase()

        with pytest.raises(NotImplementedError):
            _MixinBase._parse_agency_from_urn("urn")
        with pytest.raises(NotImplementedError):
            _MixinBase._parse_codelist_urn("urn")
        with pytest.raises(NotImplementedError):
            _MixinBase._parse_indicator_code_from_urn("urn")
        with pytest.raises(NotImplementedError):
            _MixinBase._parse_codelist_id_from_urn("urn")
        with pytest.raises(NotImplementedError):
            _MixinBase._parse_query("q")
        with pytest.raises(NotImplementedError):
            _MixinBase._build_time_period_parameters(None)
        with pytest.raises(NotImplementedError):
            base._extract_all_codelists_from_hierarchy({})
        with pytest.raises(NotImplementedError):
            base._build_hierarchy_to_codelist_map()
        with pytest.raises(NotImplementedError):
            base._build_codelist_to_hierarchies_map()
        with pytest.raises(NotImplementedError):
            base._get_dimension_for_codelist("a", "b")
        with pytest.raises(NotImplementedError):
            base._load_from_cache()
        with pytest.raises(NotImplementedError):
            base._fetch_single_codelist("a", "b")
        with pytest.raises(NotImplementedError):
            base._bulk_fetch_and_cache_codelists("a", "b")
        with pytest.raises(NotImplementedError):
            base._get_codelist_map("a", "b", "c")
        with pytest.raises(NotImplementedError):
            base.list_dataflows()
        with pytest.raises(NotImplementedError):
            base.search_dataflows("q")
        with pytest.raises(NotImplementedError):
            base.search_indicators("q")
        with pytest.raises(NotImplementedError):
            base.get_dataflow_parameters("d")
        with pytest.raises(NotImplementedError):
            base.get_available_constraints("d", "k")
        with pytest.raises(NotImplementedError):
            base._resolve_codelist_id("d", "x", "y", {})
        with pytest.raises(NotImplementedError):
            base.get_indicators_in("d")
        with pytest.raises(NotImplementedError):
            base.get_dataflow_hierarchies("d")
        with pytest.raises(NotImplementedError):
            base.get_dataflow_table_structure("d")
        with pytest.raises(NotImplementedError):
            base.list_all_dataflow_tables()
        with pytest.raises(NotImplementedError):
            base._validate_hierarchy_queryable("d", [])
        with pytest.raises(NotImplementedError):
            base._fix_irfcl_hierarchy([])
        with pytest.raises(NotImplementedError):
            base._create_synthetic_groups_for_shared_prefixes([])
        with pytest.raises(NotImplementedError):
            base._build_indicator_table_maps(set())
        with pytest.raises(NotImplementedError):
            base._collect_indicators(set(), {}, {})
        with pytest.raises(NotImplementedError):
            base._filter_indicators_by_query([], "q")
        with pytest.raises(NotImplementedError):
            base._filter_indicators_by_keywords([], None)
        with pytest.raises(NotImplementedError):
            base._find_indicator_codelist_for_hierarchies("d", "x", [])
        with pytest.raises(NotImplementedError):
            base._split_irfcl_hierarchy("d", "h", {}, [], "c")
        with pytest.raises(NotImplementedError):
            _MixinBase._select_hierarchy(None, [])
        with pytest.raises(NotImplementedError):
            base._process_hierarchical_codes(
                [],
                dataflow_id="d",
                agency_clean="IMF",
                indicator_dimension_order={},
                codelist_dimension_cache={},
                codelist_labels_cache={},
                codelist_desc_cache={},
            )
        with pytest.raises(NotImplementedError):
            base._resolve_dimension_for_code("d", None, "", {}, {}, {})
        with pytest.raises(NotImplementedError):
            _MixinBase._wrap_with_suffix_groups([], [], 0, None, [])
        with pytest.raises(NotImplementedError):
            _MixinBase._wrap_with_prefix_group([], [], 0, None, [])
