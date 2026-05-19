"""Tests for ``openbb_quantitative.performance`` - performance-metric commands."""

from math import isfinite, isnan

from openbb_quantitative import performance


def test_query_params_defaults():
    """The performance QueryParams expose the documented default values."""
    omega = performance.OmegaRatioQueryParams(data=[], target="close")
    assert omega.threshold_start == 0.0
    assert omega.threshold_end == 1.5
    assert omega.bins == 50

    sharpe = performance.SharpeRatioQueryParams(data=[], target="close")
    assert sharpe.rfr == 0.0
    assert sharpe.window == 252
    assert sharpe.index == "date"

    sortino = performance.SortinoRatioQueryParams(data=[], target="close")
    assert sortino.target_return == 0.0
    assert sortino.window == 252
    assert sortino.adjusted is False
    assert sortino.index == "date"


def test_omega_ratio(prices_data):
    """The Omega ratio returns one finite ratio per threshold across 50 thresholds."""
    params = performance.OmegaRatioQueryParams(data=prices_data, target="close")
    out = performance.omega_ratio(params)
    results = out.results
    assert isinstance(results, list)
    assert len(results) == 50
    for row in results:
        assert isinstance(row, performance.OmegaRatioData)
        assert isfinite(row.threshold)
        assert isfinite(row.omega)


def test_omega_ratio_bins(prices_data):
    """The Omega ratio honors an explicit threshold count."""
    out = performance.omega_ratio(
        performance.OmegaRatioQueryParams(data=prices_data, target="close", bins=10)
    )
    assert len(out.results) == 10


def test_sharpe_ratio(prices_data):
    """The rolling Sharpe ratio returns finite dated observations."""
    params = performance.SharpeRatioQueryParams(
        data=prices_data, target="close", window=20
    )
    out = performance.sharpe_ratio(params)
    results = out.results
    assert isinstance(results, list)
    assert len(results) > 0
    for row in results:
        assert isinstance(row, performance.SharpeRatioData)
        assert row.date is not None
        assert isfinite(row.sharpe_ratio)


def test_sortino_ratio(prices_data):
    """The rolling Sortino ratio returns dated numeric observations."""
    params = performance.SortinoRatioQueryParams(
        data=prices_data, target="close", window=20
    )
    out = performance.sortino_ratio(params)
    results = out.results
    assert isinstance(results, list)
    assert len(results) > 0
    for row in results:
        assert isinstance(row, performance.SortinoRatioData)
        assert row.date is not None
        assert isfinite(row.sortino_ratio)


def test_sortino_ratio_adjusted(prices_data):
    """The adjusted Sortino ratio scales the unadjusted ratio by 1/sqrt(2)."""
    from math import sqrt

    unadjusted = performance.sortino_ratio(
        performance.SortinoRatioQueryParams(
            data=prices_data, target="close", window=20, adjusted=False
        )
    ).results
    adjusted = performance.sortino_ratio(
        performance.SortinoRatioQueryParams(
            data=prices_data, target="close", window=20, adjusted=True
        )
    ).results
    assert len(adjusted) == len(unadjusted)
    assert len(adjusted) > 0
    for adj, unadj in zip(adjusted, unadjusted):
        assert not isnan(adj.sortino_ratio)
        assert adj.sortino_ratio == unadj.sortino_ratio / sqrt(2)
