"""Coverage tests for OecdParamsBuilder."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_oecd.utils.progressive_helper import OecdParamsBuilder

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


@pytest.fixture
def builder(seeded_meta, monkeypatch):
    """Construct an OecdParamsBuilder wired to seeded_meta."""
    monkeypatch.setattr(
        type(seeded_meta), "_ensure_structure", lambda self, fid, force=False: None
    )
    monkeypatch.setattr(
        type(seeded_meta),
        "fetch_availability",
        lambda self, fid, pinned=None: {
            "REF_AREA": ["USA", "GBR"],
            "MEASURE": ["CPI"],
            "FREQ": ["A", "Q"],
        },
    )
    return OecdParamsBuilder(_SHORT_ID)


class TestInit:
    def test_dimensions_in_order(self, builder):
        assert builder.get_dimensions_in_order() == ["REF_AREA", "MEASURE", "FREQ"]

    def test_initial_state(self, builder):
        assert all(v is None for v in builder.get_dimensions().values())
        assert builder.current_dimension == "REF_AREA"


class TestSetDimension:
    def test_pins_value_and_clears_downstream(self, builder):
        builder.set_dimension(("REF_AREA", "USA"))
        builder.set_dimension(("MEASURE", "CPI"))
        builder.set_dimension(("REF_AREA", "GBR"))
        assert builder.pinned == {"REF_AREA": "GBR"}

    def test_unknown_dimension_raises(self, builder):
        with pytest.raises(KeyError, match="not valid"):
            builder.set_dimension(("UNKNOWN", "X"))

    def test_current_dimension_updates(self, builder):
        builder.set_dimension(("REF_AREA", "USA"))
        assert builder.current_dimension == "MEASURE"


class TestGetOptionsForDimension:
    def test_default_returns_next_dim_options(self, builder):
        opts = builder.get_options_for_dimension()
        assert {o["value"] for o in opts} == {"USA", "GBR"}

    def test_explicit_dim_id(self, builder):
        opts = builder.get_options_for_dimension("MEASURE")
        assert {o["value"] for o in opts} == {"CPI"}

    def test_no_next_dim_returns_empty(self, builder):
        builder.set_dimension(("REF_AREA", "USA"))
        builder.set_dimension(("MEASURE", "CPI"))
        builder.set_dimension(("FREQ", "A"))
        assert builder.get_options_for_dimension() == []

    def test_unknown_dim_raises(self, builder):
        with pytest.raises(ValueError, match="not found"):
            builder.get_options_for_dimension("UNKNOWN")

    def test_labels_filled_from_codelist(self, builder, monkeypatch):
        monkeypatch.setattr(
            type(builder._metadata),
            "get_codelist_for_dimension",
            lambda self, fid, dim: {"USA": "United States", "GBR": "United Kingdom"},
        )
        opts = builder.get_options_for_dimension("REF_AREA")
        labels = {o["value"]: o["label"] for o in opts}
        assert labels["USA"] == "United States"


class TestDimensionsProperty:
    def test_dimensions_returns_list_copy(self, builder):
        dims = builder.dimensions
        dims.append("EXTRA")
        assert builder.dimensions == ["REF_AREA", "MEASURE", "FREQ"]


class TestAvailableAndAvailableValues:
    def test_available_alias(self, builder):
        opts = builder.available("REF_AREA")
        assert {o["value"] for o in opts} == {"USA", "GBR"}

    def test_available_values_returns_codes(self, builder):
        codes = builder.available_values("REF_AREA")
        assert set(codes) == {"USA", "GBR"}

    def test_available_values_unknown_dim_raises(self, builder):
        with pytest.raises(OpenBBError, match="not a dimension"):
            builder.available_values("UNKNOWN")


class TestSet:
    def test_chainable(self, builder):
        result = builder.set("REF_AREA", "USA")
        assert result is builder
        assert builder.pinned == {"REF_AREA": "USA"}

    def test_multi_value(self, builder):
        builder.set("REF_AREA", "USA+GBR")
        assert builder.pinned["REF_AREA"] == "USA+GBR"

    def test_invalid_value_raises(self, builder, monkeypatch):
        monkeypatch.setattr(
            type(builder._metadata),
            "get_codelist_for_dimension",
            lambda self, fid, dim: {"USA": "United States", "GBR": "United Kingdom"},
        )
        with pytest.raises(OpenBBError, match="Invalid value"):
            builder.set("REF_AREA", "ZZZ")

    def test_unknown_dim_raises(self, builder):
        with pytest.raises(OpenBBError, match="not a dimension"):
            builder.set("UNKNOWN", "X")

    def test_downstream_cleared(self, builder):
        builder.set("REF_AREA", "USA")
        builder.set("MEASURE", "CPI")
        builder.set("REF_AREA", "GBR")
        assert builder.pinned == {"REF_AREA": "GBR"}

    def test_truncated_sample_with_ellipsis(self, builder, monkeypatch):
        many_codes = [f"C{i}" for i in range(30)]
        monkeypatch.setattr(
            type(builder._metadata),
            "fetch_availability",
            lambda self, fid, pinned=None: {"REF_AREA": many_codes},
        )
        monkeypatch.setattr(
            type(builder._metadata),
            "get_codelist_for_dimension",
            lambda self, fid, dim: {c: c for c in many_codes},
        )
        with pytest.raises(OpenBBError, match=" …"):
            builder.set("REF_AREA", "ZZZ")


class TestUnsetAndReset:
    def test_unset_removes_pin(self, builder):
        builder.set("REF_AREA", "USA")
        builder.unset("REF_AREA")
        assert builder.pinned == {}

    def test_unset_unknown_dim_is_noop(self, builder):
        result = builder.unset("UNKNOWN")
        assert result is builder

    def test_reset_clears_all(self, builder):
        builder.set("REF_AREA", "USA")
        builder.set("MEASURE", "CPI")
        builder.reset()
        assert builder.pinned == {}


class TestDescribeAndSummary:
    def test_describe_returns_one_entry_per_dim(self, builder, monkeypatch):
        monkeypatch.setattr(
            type(builder._metadata),
            "get_table_parameters",
            lambda self, fid: {
                "REF_AREA": {
                    "name": "Reference Area",
                    "position": 1,
                    "role": "country",
                },
                "MEASURE": {"name": "Measure", "position": 2, "role": "selector"},
                "FREQ": {"name": "Frequency", "position": 3, "role": "freq"},
            },
        )
        monkeypatch.setattr(
            type(builder._metadata),
            "get_codelist_for_dimension",
            lambda self, fid, dim: {"USA": "United States"},
        )
        rows = builder.describe()
        assert {r["id"] for r in rows} == {"REF_AREA", "MEASURE", "FREQ"}
        ref = next(r for r in rows if r["id"] == "REF_AREA")
        assert ref["role"] == "country"
        assert ref["available"]

    def test_summary_compact_shape(self, builder, monkeypatch):
        monkeypatch.setattr(
            type(builder._metadata),
            "get_table_parameters",
            lambda self, fid: {
                "REF_AREA": {"name": "Reference Area", "role": "country"},
            },
        )
        rows = builder.summary()
        for r in rows:
            assert "available_count" in r
            assert "available" not in r


class TestBuildAndUrl:
    def test_build_all_wildcards_when_empty(self, builder):
        assert builder.build() == "*.*.*.*"

    def test_build_with_pin(self, builder):
        builder.set("REF_AREA", "USA")
        parts = builder.build().split(".")
        assert parts[0] == "USA"
        assert parts[-1] == "*"

    def test_build_url_delegates(self, builder, monkeypatch):
        called = {}

        def _stub(self, fid, dimension_filter, last_n=None, first_n=None):
            called["args"] = (fid, dimension_filter, last_n, first_n)
            return "http://test"

        monkeypatch.setattr(type(builder._metadata), "build_data_url", _stub)
        url = builder.build_url(last_n=5)
        assert url == "http://test"
        assert called["args"][2] == 5


class TestFetch:
    def test_delegates_to_query_builder(self, builder):
        mock_qb = MagicMock()
        mock_qb.fetch_data.return_value = {"data": [], "metadata": {}}
        builder.set("REF_AREA", "USA")
        with patch(
            "openbb_oecd.utils.query_builder.OecdQueryBuilder", return_value=mock_qb
        ):
            result = builder.fetch(start_date="2020", end_date="2024")
        assert result == {"data": [], "metadata": {}}
        kwargs = mock_qb.fetch_data.call_args.kwargs
        assert kwargs["dataflow"] == _SHORT_ID
        assert kwargs["start_date"] == "2020"
        assert kwargs["dimension_filters"] == {"REF_AREA": "USA"}


class TestRepr:
    def test_repr_includes_dataflow_id(self, builder):
        rep = repr(builder)
        assert _SHORT_ID in rep
        assert "pinned" in rep


class TestEmptyDimensions:
    def test_no_dimensions_yields_none_current(self, seeded_meta, monkeypatch):
        seeded_meta.datastructures[_FULL_ID]["dimensions"] = []
        monkeypatch.setattr(
            type(seeded_meta), "_ensure_structure", lambda self, fid, force=False: None
        )
        builder = OecdParamsBuilder(_SHORT_ID)
        assert builder.current_dimension is None
        assert builder.get_dimensions_in_order() == []
