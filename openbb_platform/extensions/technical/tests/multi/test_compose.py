"""Tests for ``openbb_technical.multi.compose``."""

from __future__ import annotations

import pytest

from openbb_technical.multi.compose import (
    MultiIndicatorRequest,
    MultiQueryParams,
    MultiResultRow,
    _numeric_columns,
    _resolve_indicator,
    _row_key,
    _to_records,
    multi,
)


class TestResolveIndicator:
    def test_resolves_known(self):
        fn = _resolve_indicator("rsi")
        assert callable(fn)

    def test_skip_on_missing(self):
        assert _resolve_indicator("___definitely_not_a_real_indicator___") is None


class TestHelpers:
    def test_to_records_passthrough_dict(self):
        rows = _to_records([{"a": 1}])
        assert rows == [{"a": 1}]

    def test_to_records_from_pydantic(self):
        class _Row:
            def model_dump(self):
                return {"a": 2}

        assert _to_records([_Row()]) == [{"a": 2}]

    def test_to_records_unwraps_obbject(self):
        class _OBB:
            results = [{"a": 3}]

        assert _to_records(_OBB()) == [{"a": 3}]

    def test_row_key_uses_index(self):
        assert _row_key({"date": "2021-01-01", "x": 1}, "date") == "2021-01-01"

    def test_numeric_columns_drops_ohlc(self):
        row = {
            "date": "2021-01-01",
            "open": 1.0,
            "high": 1.0,
            "low": 1.0,
            "close": 1.0,
            "volume": 1.0,
            "rsi": 55.0,
            "label": "tag",
        }
        out = _numeric_columns(row, target="close")
        assert "rsi" in out
        assert "label" not in out
        assert "open" not in out

    def test_numeric_columns_passes_none(self):
        row = {"rsi": None}
        out = _numeric_columns(row, target="close")
        assert out == {"rsi": None}


class TestMultiEndpoint:
    def test_single_indicator(self, single_symbol_records):
        out = multi(
            MultiQueryParams(
                data=single_symbol_records,
                indicators=[
                    MultiIndicatorRequest(indicator="rsi", params={"length": 14})
                ],
            )
        )
        assert out.results
        assert all(isinstance(r, MultiResultRow) for r in out.results)
        assert any(r.values.get("rsi.rsi") is not None for r in out.results)

    def test_two_indicators_merge(self, single_symbol_records):
        out = multi(
            MultiQueryParams(
                data=single_symbol_records,
                indicators=[
                    MultiIndicatorRequest(indicator="rsi", params={"length": 14}),
                    MultiIndicatorRequest(indicator="atr", params={"length": 14}),
                ],
            )
        )
        assert out.results
        for row in out.results:
            if "rsi.rsi" in row.values and "atr.atr" in row.values:
                assert row.values["rsi.rsi"] is not None
                assert row.values["atr.atr"] is not None
                break
        else:  # pragma: no cover - sanity guard, fixture has 300 bars
            pytest.fail("Never found a row where both indicators warmed up.")

    def test_unknown_indicator_skipped(self, single_symbol_records):
        out = multi(
            MultiQueryParams(
                data=single_symbol_records,
                indicators=[
                    MultiIndicatorRequest(indicator="not_a_real_indicator", params={}),
                    MultiIndicatorRequest(indicator="rsi", params={"length": 14}),
                ],
            )
        )
        assert out.results
        assert all(
            all(not k.startswith("not_a_real_indicator.") for k in r.values)
            for r in out.results
        )

    def test_query_params_defaults(self, single_symbol_records):
        params = MultiQueryParams(
            data=single_symbol_records,
            indicators=[MultiIndicatorRequest(indicator="rsi")],
        )
        assert params.index == "date"
        assert params.target == "close"
