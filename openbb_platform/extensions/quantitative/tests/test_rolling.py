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


def test_rolling_factors_happy_path(target_returns_data, factor_matrix_data):
    """Rolling factors emits one row per (window-end, regressor) with finite stats."""
    params = rolling.RollingFactorsQueryParams(
        data=target_returns_data,
        factors_data=factor_matrix_data,
        target="close",
        window=252,
        step=21,
        risk_free_column="rf",
    )
    out = rolling.factors(params)
    results = out.results
    assert isinstance(results, list)
    assert results

    factors_set = {r.factor for r in results}
    assert factors_set == {"const", "f1", "f2"}
    for row in results:
        assert isinstance(row, rolling.RollingFactorsData)
        assert isfinite(row.coefficient)
        assert isfinite(row.t_statistic)


def test_rolling_factors_default_params():
    """Default ``window`` and ``step`` match the documented values."""
    params = rolling.RollingFactorsQueryParams(data=[], factors_data=[], target="close")
    assert params.window == 252
    assert params.step == 21
    assert params.index == "date"
    assert params.risk_free_column is None


def test_rolling_factors_window_too_large(target_returns_data, factor_matrix_data):
    """A window longer than the aligned data raises ValueError."""
    import pytest

    params = rolling.RollingFactorsQueryParams(
        data=target_returns_data,
        factors_data=factor_matrix_data,
        target="close",
        window=10_000,
    )
    with pytest.raises(ValueError, match="exceeds the aligned data length"):
        rolling.factors(params)


def test_rolling_factors_window_too_small(target_returns_data, factor_matrix_data):
    """A window not large enough to fit regressors+1 raises ValueError."""
    import pytest

    params = rolling.RollingFactorsQueryParams(
        data=target_returns_data,
        factors_data=factor_matrix_data,
        target="close",
        window=3,
    )
    with pytest.raises(ValueError, match="must exceed the number of regressors"):
        rolling.factors(params)
