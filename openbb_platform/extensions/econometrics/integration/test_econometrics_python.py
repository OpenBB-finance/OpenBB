"""Integration tests for the openbb-econometrics Python interface."""

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
def test_econometrics_correlation_matrix(obb, timeseries_data):
    result = obb.econometrics.correlation_matrix(data=timeseries_data, method="pearson")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_summary_statistics(obb, timeseries_data):
    result = obb.econometrics.summary_statistics(data=timeseries_data)
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_ols_regression(obb, timeseries_data):
    result = obb.econometrics.ols_regression(
        data=timeseries_data, y_column="close", x_columns=["high", "low"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_ols_regression_summary(obb, timeseries_data):
    result = obb.econometrics.ols_regression_summary(
        data=timeseries_data, y_column="close", x_columns=["high", "low"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_autocorrelation(obb, timeseries_data):
    result = obb.econometrics.autocorrelation(
        data=timeseries_data, y_column="close", x_columns=["open"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_residual_autocorrelation(obb, timeseries_data):
    result = obb.econometrics.residual_autocorrelation(
        data=timeseries_data, y_column="close", x_columns=["open"], lags=4
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_heteroskedasticity(obb, timeseries_data):
    result = obb.econometrics.heteroskedasticity(
        data=timeseries_data, y_column="close", x_columns=["open"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_normality(obb, timeseries_data):
    result = obb.econometrics.normality(
        data=timeseries_data, y_column="close", x_columns=["open"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_variance_inflation_factor(obb, timeseries_data):
    result = obb.econometrics.variance_inflation_factor(
        data=timeseries_data, columns=["open", "high", "low"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_unit_root(obb, timeseries_data):
    result = obb.econometrics.unit_root(
        data=timeseries_data, column="close", regression="c"
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_kpss(obb, timeseries_data):
    result = obb.econometrics.kpss(data=timeseries_data, column="close", regression="c")
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_cointegration(obb, timeseries_data):
    result = obb.econometrics.cointegration(
        data=timeseries_data, columns=["open", "close"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_cointegration_johansen(obb, timeseries_data):
    result = obb.econometrics.cointegration_johansen(
        data=timeseries_data, columns=["open", "high", "close"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_causality(obb, timeseries_data):
    result = obb.econometrics.causality(
        data=timeseries_data, y_column="close", x_column="volume", lag=3
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_garch(obb, timeseries_data):
    result = obb.econometrics.garch(data=timeseries_data, column="close", p=1, q=1)
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_panel_random_effects(obb, panel_data):
    result = obb.econometrics.panel_random_effects(
        data=panel_data, y_column="income", x_columns=["age", "education"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_panel_between(obb, panel_data):
    result = obb.econometrics.panel_between(
        data=panel_data, y_column="income", x_columns=["age", "education"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_panel_pooled(obb, panel_data):
    result = obb.econometrics.panel_pooled(
        data=panel_data, y_column="income", x_columns=["age", "education"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_panel_fixed(obb, panel_data):
    result = obb.econometrics.panel_fixed(
        data=panel_data, y_column="income", x_columns=["age", "education"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_panel_first_difference(obb, panel_data):
    result = obb.econometrics.panel_first_difference(
        data=panel_data, y_column="income", x_columns=["age"]
    )
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.integration
def test_econometrics_panel_fmac(obb, panel_data):
    result = obb.econometrics.panel_fmac(
        data=panel_data, y_column="income", x_columns=["age", "education"]
    )
    assert isinstance(result, OBBject)
    assert result.results
