"""Tests for ``openbb_technical.multi.correlation``."""

from __future__ import annotations

import pytest

from openbb_technical.multi.correlation import (
    CorrelationData,
    CorrelationMatrixData,
    CorrelationMatrixQueryParams,
    CorrelationQueryParams,
    correlation,
    correlation_matrix,
)


class TestCorrelation:
    def test_default_pairs_pearson(self, multi_symbol_records):
        out = correlation(CorrelationQueryParams(data=multi_symbol_records, window=30))
        assert out.results
        assert all(isinstance(r, CorrelationData) for r in out.results)
        pair_set = {(r.symbol_a, r.symbol_b) for r in out.results}
        assert pair_set == {("AAA", "BBB"), ("AAA", "CCC"), ("BBB", "CCC")}

    def test_explicit_pairs(self, multi_symbol_records):
        out = correlation(
            CorrelationQueryParams(
                data=multi_symbol_records,
                window=30,
                pairs=[("AAA", "BBB"), ("XYZ", "AAA")],
            )
        )
        assert out.results
        pair_set = {(r.symbol_a, r.symbol_b) for r in out.results}
        assert pair_set == {("AAA", "BBB")}

    @pytest.mark.parametrize("method", ["pearson", "spearman", "kendall"])
    def test_each_method(self, multi_symbol_records, method):
        out = correlation(
            CorrelationQueryParams(data=multi_symbol_records, window=30, method=method)
        )
        assert out.results
        assert any(r.correlation is not None for r in out.results)

    def test_missing_symbol_column_errors(self, single_symbol_records):
        sym_less = [
            type(r).model_validate(
                {k: v for k, v in r.model_dump().items() if k != "symbol"}
            )
            for r in single_symbol_records[:5]
        ]
        with pytest.raises(ValueError, match="symbol"):
            correlation(CorrelationQueryParams(data=sym_less, window=5))

    def test_query_params_defaults(self, multi_symbol_records):
        params = CorrelationQueryParams(data=multi_symbol_records)
        assert params.window == 60
        assert params.method == "pearson"
        assert params.target == "close"
        assert params.pairs is None


class TestCorrelationMatrix:
    def test_default_uses_last_date(self, multi_symbol_records):
        out = correlation_matrix(
            CorrelationMatrixQueryParams(data=multi_symbol_records)
        )
        assert out.results
        row = out.results[0]
        assert isinstance(row, CorrelationMatrixData)
        assert row.symbols == ["AAA", "BBB", "CCC"]
        assert row.matrix[0][0] == pytest.approx(1.0)
        assert row.matrix[1][1] == pytest.approx(1.0)

    def test_window_clipped(self, multi_symbol_records):
        out = correlation_matrix(
            CorrelationMatrixQueryParams(data=multi_symbol_records, window=60)
        )
        assert out.results
        assert len(out.results[0].symbols) == 3

    def test_explicit_as_of(self, multi_symbol_records):
        out = correlation_matrix(
            CorrelationMatrixQueryParams(
                data=multi_symbol_records, window=60, as_of_date="2021-12-31"
            )
        )
        assert out.results
        assert str(out.results[0].as_of_date) <= "2021-12-31"

    @pytest.mark.parametrize("method", ["pearson", "spearman", "kendall"])
    def test_each_method(self, multi_symbol_records, method):
        out = correlation_matrix(
            CorrelationMatrixQueryParams(data=multi_symbol_records, method=method)
        )
        assert out.results

    def test_missing_symbol_column_errors(self, single_symbol_records):
        sym_less = [
            type(r).model_validate(
                {k: v for k, v in r.model_dump().items() if k != "symbol"}
            )
            for r in single_symbol_records[:5]
        ]
        with pytest.raises(ValueError, match="symbol"):
            correlation_matrix(CorrelationMatrixQueryParams(data=sym_less))

    def test_query_params_defaults(self, multi_symbol_records):
        params = CorrelationMatrixQueryParams(data=multi_symbol_records)
        assert params.window is None
        assert params.method == "pearson"
        assert params.as_of_date is None
