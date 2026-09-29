"""Tests for ``openbb_econometrics.tools`` - correlation matrix and statistics."""

import pytest

from openbb_econometrics import tools


@pytest.mark.parametrize("method", ["pearson", "kendall", "spearman"])
def test_correlation_matrix_methods(timeseries_data, method):
    """The correlation matrix returns one row per numeric column for each method."""
    out = tools.correlation_matrix(
        tools.CorrelationMatrixQueryParams(data=timeseries_data, method=method)
    )
    results = out.results
    assert isinstance(results, list)
    # open/high/low/close/volume -> 5 numeric columns.
    assert len(results) == 5
    comp_to = {row.comp_to for row in results}
    assert comp_to == {"open", "high", "low", "close", "volume"}
    for row in results:
        dumped = row.model_dump()
        assert dumped["comp_to"] in comp_to
        # The self-correlation is 1.0.
        assert dumped[row.comp_to] == pytest.approx(1.0)


def test_correlation_matrix_defaults(timeseries_data):
    """The correlation matrix defaults to the pearson method with min_periods of 1."""
    params = tools.CorrelationMatrixQueryParams(data=timeseries_data)
    assert params.method == "pearson"
    assert params.min_periods == 1
    out = tools.correlation_matrix(params)
    assert len(out.results) == 5


def test_correlation_matrix_min_periods(timeseries_data):
    """The correlation matrix honours an explicit min_periods threshold."""
    out = tools.correlation_matrix(
        tools.CorrelationMatrixQueryParams(data=timeseries_data, min_periods=10)
    )
    assert len(out.results) == 5


def test_correlation_matrix_symbol_pivot(symbol_data):
    """A dataset with a ``symbol`` column and >1 symbol pivots on ``close``."""
    out = tools.correlation_matrix(tools.CorrelationMatrixQueryParams(data=symbol_data))
    results = out.results
    # Pivoted on the three symbols.
    assert len(results) == 3
    assert {row.comp_to for row in results} == {"AAA", "BBB", "CCC"}


def test_summary_statistics(timeseries_data):
    """Summary statistics returns one fully-populated row per numeric column."""
    out = tools.summary_statistics(
        tools.SummaryStatisticsQueryParams(data=timeseries_data)
    )
    results = out.results
    assert len(results) == 5
    columns = {row.column for row in results}
    assert columns == {"open", "high", "low", "close", "volume"}
    for row in results:
        dumped = row.model_dump()
        assert dumped["count"] > 0
        assert dumped["min"] <= dumped["median"] <= dumped["max"]
        assert dumped["p25"] <= dumped["p75"]
        assert isinstance(dumped["skew"], float)
        assert isinstance(dumped["kurtosis"], float)
