"""Integration tests for the openbb-quantitative Python interface."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Return the obb application object for the integration session."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb
    return None


@pytest.mark.integration
def test_quantitative_normality(obb, prices_data):
    result = obb.quantitative.normality(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_capm(obb, prices_data):
    result = obb.quantitative.capm(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_unitroot_test(obb, prices_data):
    result = obb.quantitative.unitroot_test(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_summary(obb, prices_data):
    result = obb.quantitative.summary(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_rolling_skew(obb, prices_data):
    result = obb.quantitative.rolling.skew(data=prices_data, target="close", window=20)
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_rolling_variance(obb, prices_data):
    result = obb.quantitative.rolling.variance(
        data=prices_data, target="close", window=20
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_rolling_stdev(obb, prices_data):
    result = obb.quantitative.rolling.stdev(data=prices_data, target="close", window=20)
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_rolling_kurtosis(obb, prices_data):
    result = obb.quantitative.rolling.kurtosis(
        data=prices_data, target="close", window=20
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_rolling_mean(obb, prices_data):
    result = obb.quantitative.rolling.mean(data=prices_data, target="close", window=20)
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_rolling_quantile(obb, prices_data):
    result = obb.quantitative.rolling.quantile(
        data=prices_data, target="close", window=20, quantile_pct=0.75
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_stats_skew(obb, prices_data):
    result = obb.quantitative.stats.skew(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_stats_variance(obb, prices_data):
    result = obb.quantitative.stats.variance(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_stats_stdev(obb, prices_data):
    result = obb.quantitative.stats.stdev(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_stats_kurtosis(obb, prices_data):
    result = obb.quantitative.stats.kurtosis(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_stats_mean(obb, prices_data):
    result = obb.quantitative.stats.mean(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_stats_quantile(obb, prices_data):
    result = obb.quantitative.stats.quantile(
        data=prices_data, target="close", quantile_pct=0.75
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_performance_omega_ratio(obb, prices_data):
    result = obb.quantitative.performance.omega_ratio(data=prices_data, target="close")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_performance_sharpe_ratio(obb, prices_data):
    result = obb.quantitative.performance.sharpe_ratio(
        data=prices_data, target="close", window=20
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_quantitative_performance_sortino_ratio(obb, prices_data):
    result = obb.quantitative.performance.sortino_ratio(
        data=prices_data, target="close", window=20
    )
    assert isinstance(result, OBBject)
    assert result.results
