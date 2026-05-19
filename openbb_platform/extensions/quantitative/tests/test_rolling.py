"""Tests for ``openbb_quantitative.rolling`` - rolling-statistics commands."""

from math import isfinite

from openbb_quantitative import rolling


def test_rolling_skew(prices_data):
    """Rolling skew returns finite values for each completed window."""
    params = rolling.RollingSkewQueryParams(data=prices_data, target="close", window=20)
    out = rolling.skew(params)
    results = out.results
    assert isinstance(results, list)
    assert results
    for row in results:
        assert isinstance(row, rolling.RollingSkewData)
        assert isfinite(row.skew)
        assert row.date is not None


def test_rolling_variance(prices_data):
    """Rolling variance returns finite, non-negative values."""
    params = rolling.RollingVarianceQueryParams(
        data=prices_data, target="close", window=20
    )
    out = rolling.variance(params)
    results = out.results
    assert isinstance(results, list)
    assert results
    for row in results:
        assert isinstance(row, rolling.RollingVarianceData)
        assert isfinite(row.variance)
        assert row.variance >= 0.0
        assert row.date is not None


def test_rolling_stdev(prices_data):
    """Rolling standard deviation returns finite, non-negative values."""
    params = rolling.RollingStdevQueryParams(
        data=prices_data, target="close", window=20
    )
    out = rolling.stdev(params)
    results = out.results
    assert isinstance(results, list)
    assert results
    for row in results:
        assert isinstance(row, rolling.RollingStdevData)
        assert isfinite(row.stdev)
        assert row.stdev >= 0.0
        assert row.date is not None


def test_rolling_kurtosis(prices_data):
    """Rolling kurtosis returns finite values for each completed window."""
    params = rolling.RollingKurtosisQueryParams(
        data=prices_data, target="close", window=20
    )
    out = rolling.kurtosis(params)
    results = out.results
    assert isinstance(results, list)
    assert results
    for row in results:
        assert isinstance(row, rolling.RollingKurtosisData)
        assert isfinite(row.kurtosis)
        assert row.date is not None


def test_rolling_mean(prices_data):
    """Rolling mean returns finite values for each completed window."""
    params = rolling.RollingMeanQueryParams(data=prices_data, target="close", window=20)
    out = rolling.mean(params)
    results = out.results
    assert isinstance(results, list)
    assert results
    for row in results:
        assert isinstance(row, rolling.RollingMeanData)
        assert isfinite(row.mean)
        assert row.date is not None


def test_rolling_quantile(prices_data):
    """Rolling quantile returns finite median and quantile values."""
    params = rolling.RollingQuantileQueryParams(
        data=prices_data, target="close", window=20
    )
    out = rolling.quantile(params)
    results = out.results
    assert isinstance(results, list)
    assert results
    for row in results:
        assert isinstance(row, rolling.RollingQuantileData)
        assert isfinite(row.median)
        assert isfinite(row.quantile)
        assert row.date is not None


def test_rolling_query_params_defaults():
    """The rolling QueryParams expose the documented default values."""
    skew_params = rolling.RollingSkewQueryParams(data=[], target="close")
    assert skew_params.window == 21
    assert skew_params.index == "date"
    variance_params = rolling.RollingVarianceQueryParams(data=[], target="close")
    assert variance_params.window == 21
    assert variance_params.index == "date"
    stdev_params = rolling.RollingStdevQueryParams(data=[], target="close")
    assert stdev_params.window == 21
    assert stdev_params.index == "date"
    kurtosis_params = rolling.RollingKurtosisQueryParams(data=[], target="close")
    assert kurtosis_params.window == 21
    assert kurtosis_params.index == "date"
    mean_params = rolling.RollingMeanQueryParams(data=[], target="close")
    assert mean_params.window == 21
    assert mean_params.index == "date"
    quantile_params = rolling.RollingQuantileQueryParams(data=[], target="close")
    assert quantile_params.window == 21
    assert quantile_params.index == "date"
    assert quantile_params.quantile_pct == 0.5
