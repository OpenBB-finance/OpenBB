"""Tests for ``openbb_quantitative.stats`` - summary statistics commands."""

import math

from openbb_quantitative import stats


def test_skew(prices_data):
    """The skew command returns a finite skewness value."""
    out = stats.skew(stats.StatsSkewQueryParams(data=prices_data, target="close"))
    result = out.results
    assert isinstance(result, stats.StatsSkewData)
    assert isinstance(result.skew, float)
    assert math.isfinite(result.skew)


def test_variance(prices_data):
    """The variance command returns a finite, non-negative variance value."""
    out = stats.variance(
        stats.StatsVarianceQueryParams(data=prices_data, target="close")
    )
    result = out.results
    assert isinstance(result, stats.StatsVarianceData)
    assert isinstance(result.variance, float)
    assert math.isfinite(result.variance)
    assert result.variance >= 0.0


def test_stdev(prices_data):
    """The stdev command returns a finite, non-negative standard deviation."""
    out = stats.stdev(stats.StatsStdevQueryParams(data=prices_data, target="close"))
    result = out.results
    assert isinstance(result, stats.StatsStdevData)
    assert isinstance(result.stdev, float)
    assert math.isfinite(result.stdev)
    assert result.stdev >= 0.0


def test_kurtosis(prices_data):
    """The kurtosis command returns a finite kurtosis value."""
    out = stats.kurtosis(
        stats.StatsKurtosisQueryParams(data=prices_data, target="close")
    )
    result = out.results
    assert isinstance(result, stats.StatsKurtosisData)
    assert isinstance(result.kurtosis, float)
    assert math.isfinite(result.kurtosis)


def test_mean(prices_data):
    """The mean command returns a finite arithmetic mean."""
    out = stats.mean(stats.StatsMeanQueryParams(data=prices_data, target="close"))
    result = out.results
    assert isinstance(result, stats.StatsMeanData)
    assert isinstance(result.mean, float)
    assert math.isfinite(result.mean)


def test_quantile_default(prices_data):
    """The quantile command defaults to the median (0.5 quantile)."""
    params = stats.StatsQuantileQueryParams(data=prices_data, target="close")
    assert params.quantile_pct == 0.5
    out = stats.quantile(params)
    result = out.results
    assert isinstance(result, stats.StatsQuantileData)
    assert isinstance(result.median, float)
    assert isinstance(result.quantile, float)
    assert math.isfinite(result.median)
    assert math.isfinite(result.quantile)
    assert result.quantile == result.median


def test_quantile_explicit(prices_data):
    """The quantile command honors an explicit quantile percentage."""
    params = stats.StatsQuantileQueryParams(
        data=prices_data, target="close", quantile_pct=0.9
    )
    assert params.quantile_pct == 0.9
    out = stats.quantile(params)
    result = out.results
    assert isinstance(result, stats.StatsQuantileData)
    assert math.isfinite(result.quantile)
    assert result.quantile >= result.median
