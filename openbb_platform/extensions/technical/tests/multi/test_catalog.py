"""Tests for ``openbb_technical.multi.catalog``."""

from __future__ import annotations

from typing import Literal

import pytest
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_technical.multi.catalog import (
    _CATALOG,
    IndicatorEntry,
    IndicatorOutputColumn,
    IndicatorParam,
    IndicatorsQueryParams,
    IndicatorsResponse,
    _build_catalog,
    _catalog,
    _default_for,
    _example_call,
    _field_constraints,
    _find_data_model,
    _literal_choices,
    _match_query_params_for,
    _module_query_params,
    _output_column_entries,
    _required_data_columns,
    _stringify_type,
    indicators,
)


class TestStringifyType:
    def test_basic(self):
        assert _stringify_type(int) == "<class 'int'>"

    def test_optional_literal(self):
        assert "Literal" in _stringify_type(Literal["a", "b"])


class TestLiteralChoices:
    def test_direct(self):
        assert _literal_choices(Literal["a", "b"]) == ["a", "b"]

    def test_nested(self):
        assert _literal_choices(Literal["x"] | None) == ["x"]

    def test_none(self):
        assert _literal_choices(int) is None


class TestFieldConstraints:
    def test_extracts_gt(self):
        class _Q(QueryParams):
            x: int = Field(default=1, gt=0)

        out = _field_constraints(_Q.model_fields["x"])
        assert out is not None
        assert out.get("gt") == 0

    def test_returns_none_when_empty(self):
        class _Q(QueryParams):
            x: int = 1

        assert _field_constraints(_Q.model_fields["x"]) is None

    def test_extracts_direct_attribute(self):
        """Cover the Pydantic-V1-style direct attribute branch."""

        class _Stub:
            gt = 5
            metadata = ()

        out = _field_constraints(_Stub())  # type: ignore[arg-type]
        assert out == {"gt": 5}


class TestDefaultFor:
    def test_default(self):
        class _Q(QueryParams):
            x: int = 7

        assert _default_for(_Q.model_fields["x"]) == 7

    def test_required(self):
        class _Q(QueryParams):
            x: int = Field()

        assert _default_for(_Q.model_fields["x"]) is None

    def test_factory(self):
        class _Q(QueryParams):
            x: list[int] = Field(default_factory=lambda: [1, 2])

        assert _default_for(_Q.model_fields["x"]) == [1, 2]


class TestModuleHelpers:
    def test_module_query_params_finds_classes(self):
        from openbb_technical.indicators import volatility as mod

        candidates = _module_query_params(mod)
        assert "RealizedVolatilityQueryParams" in candidates

    def test_match_query_params(self):
        candidates = {"RsiQueryParams": object, "MacdQueryParams": object}
        assert (
            _match_query_params_for("rsi", candidates) is candidates["RsiQueryParams"]
        )

    def test_match_query_params_missing(self):
        assert _match_query_params_for("nope", {}) is None

    def test_find_data_model(self):
        from openbb_technical.indicators import volatility as mod

        assert _find_data_model(mod, "atr") is mod.AtrData

    def test_find_data_model_missing(self):
        from openbb_technical.indicators import volatility as mod

        assert _find_data_model(mod, "not_an_endpoint") is None


class TestOutputColumns:
    def test_columns_from_data_model(self):
        from openbb_technical.indicators.volatility import (
            AtrData,
            AtrQueryParams,
        )

        cols = _output_column_entries(AtrQueryParams, AtrData)
        names = [c.name for c in cols]
        assert "date" in names
        assert "atr" in names

    def test_columns_without_data_model(self):
        class _Q(QueryParams):
            __category__ = "test"
            __output_columns__ = ("a", "b")

        cols = _output_column_entries(_Q, None)
        assert [c.name for c in cols] == ["a", "b"]


class TestRequiredDataColumns:
    def test_picks_up_mentions(self):
        class _Q(QueryParams):
            """Needs the high and low columns."""

        assert "high" in _required_data_columns(_Q)
        assert "low" in _required_data_columns(_Q)


class TestExampleCall:
    def test_includes_defaults(self):
        from openbb_technical.indicators.volatility import RealizedVolatilityQueryParams

        ex = _example_call("realized_volatility", RealizedVolatilityQueryParams)
        assert ex["endpoint"] == "realized_volatility"
        assert ex["window"] == 30


class TestCatalog:
    def test_non_empty(self):
        assert _CATALOG, "catalog should not be empty"

    def test_index_access(self):
        first = _CATALOG[0]
        assert isinstance(first, IndicatorEntry)

    def test_catalog_helper_returns_cached(self):
        first = _catalog()
        second = _catalog()
        assert first is second

    def test_endpoint_without_query_params_is_skipped(self, monkeypatch):
        """When an endpoint has no ``XxxQueryParams`` sibling it is skipped."""
        from openbb_core.app.router import Router

        from openbb_technical.multi import catalog as catalog_module

        skip_router = Router(prefix="", description="")

        @skip_router.command(methods=["POST"])
        def lonely_endpoint(data: list = []) -> dict:  # noqa: B006
            return {}  # pragma: no cover - never called

        stub_module = type(
            "stub_mod",
            (),
            {"__name__": "stub_mod", "router": skip_router},
        )

        original = catalog_module._FAMILY_MODULES
        monkeypatch.setattr(catalog_module, "_FAMILY_MODULES", ("stub_mod",))

        import sys

        sys.modules["stub_mod"] = stub_module  # type: ignore[assignment]
        try:
            built = catalog_module._build_catalog()
        finally:
            sys.modules.pop("stub_mod", None)
            monkeypatch.setattr(catalog_module, "_FAMILY_MODULES", original)

        assert built == []

    def test_every_entry_populated(self):
        for entry in _CATALOG:
            assert isinstance(entry, IndicatorEntry)
            assert entry.name
            assert entry.category
            assert isinstance(entry.params, list)
            assert isinstance(entry.output_columns, list)
            assert isinstance(entry.example_call, dict)
            for p in entry.params:
                assert isinstance(p, IndicatorParam)
                assert p.name
                assert p.type
            for c in entry.output_columns:
                assert isinstance(c, IndicatorOutputColumn)
                assert c.name
                assert c.type

    def test_rebuild_idempotent(self):
        rebuilt = _build_catalog()
        names = sorted(e.name for e in _CATALOG)
        rebuilt_names = sorted(e.name for e in rebuilt)
        assert names == rebuilt_names


class TestIndicatorsEndpoint:
    def test_all(self):
        out = indicators(IndicatorsQueryParams(category="all"))
        assert isinstance(out.results, IndicatorsResponse)
        assert out.results.indicators

    def test_filter_volatility(self):
        out = indicators(IndicatorsQueryParams(category="volatility"))
        assert all(e.category == "volatility" for e in out.results.indicators)
        names = {e.name for e in out.results.indicators}
        assert "atr" in names

    def test_filter_none_treats_as_all(self):
        out = indicators(IndicatorsQueryParams(category=None))
        assert len(out.results.indicators) == len(_CATALOG)

    def test_filter_no_match(self):
        params = IndicatorsQueryParams(category="all")
        assert params.category == "all"


class TestQueryParams:
    def test_defaults(self):
        params = IndicatorsQueryParams()
        assert params.category == "all"

    def test_invalid_category(self):
        with pytest.raises(Exception):
            IndicatorsQueryParams(category="not_a_category")
