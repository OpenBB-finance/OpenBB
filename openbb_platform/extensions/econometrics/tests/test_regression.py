"""Tests for ``openbb_econometrics.regression`` - OLS regression commands."""

import pytest

from openbb_econometrics import regression


def test_ols_regression(timeseries_data):
    """OLS regression returns one coefficient row per regressor plus the constant."""
    params = regression.OlsRegressionQueryParams(
        data=timeseries_data,
        y_column="close",
        x_columns=["open", "high", "low"],
    )
    assert params.cov_type == "nonrobust"
    out = regression.ols_regression(params)
    results = out.results
    assert isinstance(results, list)
    # const + open + high + low.
    assert len(results) == 4
    variables = {row.variable for row in results}
    assert variables == {"const", "open", "high", "low"}
    for row in results:
        dumped = row.model_dump()
        assert dumped["conf_int_lower"] <= dumped["conf_int_upper"]
        assert isinstance(dumped["coefficient"], float)
        assert isinstance(dumped["t_statistic"], float)
        assert isinstance(dumped["p_value"], float)


def test_ols_regression_summary(timeseries_data):
    """The OLS summary reports finite goodness-of-fit statistics."""
    out = regression.ols_regression_summary(
        regression.OlsRegressionSummaryQueryParams(
            data=timeseries_data,
            y_column="close",
            x_columns=["open", "high", "low"],
        )
    )
    result = out.results
    dumped = result.model_dump()
    assert 0.0 <= dumped["r_squared"] <= 1.0
    assert dumped["nobs"] == 120
    assert dumped["f_statistic"] is not None
    assert dumped["f_p_value"] is not None
    assert isinstance(dumped["aic"], float)
    assert isinstance(dumped["bic"], float)
    assert "OLS Regression Results" in dumped["summary"]


def test_ols_regression_summary_non_numeric_raises(non_numeric_data):
    """A non-numeric regressor column triggers the numeric-coercion ValueError."""
    params = regression.OlsRegressionSummaryQueryParams(
        data=non_numeric_data,
        y_column="close",
        x_columns=["open", "high"],
    )
    with pytest.raises(ValueError, match="All columns must be numeric."):
        regression.ols_regression_summary(params)


@pytest.mark.parametrize("cov_type", ["nonrobust", "HC0", "HC1", "HC2", "HC3"])
def test_ols_regression_cov_type(timeseries_data, cov_type):
    """OLS regression accepts the nonrobust and heteroskedasticity-robust estimators."""
    out = regression.ols_regression(
        regression.OlsRegressionQueryParams(
            data=timeseries_data,
            y_column="close",
            x_columns=["open", "high", "low"],
            cov_type=cov_type,
        )
    )
    assert len(out.results) == 4


def test_ols_regression_summary_cov_type(timeseries_data):
    """The OLS summary accepts a heteroskedasticity-robust covariance estimator."""
    out = regression.ols_regression_summary(
        regression.OlsRegressionSummaryQueryParams(
            data=timeseries_data,
            y_column="close",
            x_columns=["open", "high", "low"],
            cov_type="HC3",
        )
    )
    assert 0.0 <= out.results.r_squared <= 1.0
