"""Tests for ``openbb_econometrics.diagnostics`` - regression diagnostics."""

from openbb_econometrics import diagnostics

X_COLUMNS = ["open", "high", "low"]


def test_autocorrelation(timeseries_data):
    """The Durbin-Watson statistic lies in the [0, 4] range."""
    out = diagnostics.autocorrelation(
        diagnostics.AutocorrelationQueryParams(
            data=timeseries_data, y_column="close", x_columns=X_COLUMNS
        )
    )
    result = out.results
    dumped = result.model_dump()
    assert 0.0 <= dumped["durbin_watson"] <= 4.0


def test_residual_autocorrelation(timeseries_data):
    """The Breusch-Godfrey test returns LM and F statistics with p-values."""
    out = diagnostics.residual_autocorrelation(
        diagnostics.ResidualAutocorrelationQueryParams(
            data=timeseries_data,
            y_column="close",
            x_columns=X_COLUMNS,
            lags=2,
        )
    )
    dumped = out.results.model_dump()
    assert 0.0 <= dumped["lm_p_value"] <= 1.0
    assert 0.0 <= dumped["f_p_value"] <= 1.0
    assert isinstance(dumped["lm_statistic"], float)
    assert isinstance(dumped["f_statistic"], float)


def test_residual_autocorrelation_default_lags(timeseries_data):
    """The ``lags`` parameter defaults to 1."""
    params = diagnostics.ResidualAutocorrelationQueryParams(
        data=timeseries_data, y_column="close", x_columns=X_COLUMNS
    )
    assert params.lags == 1
    out = diagnostics.residual_autocorrelation(params)
    assert out.results.lm_statistic is not None


def test_heteroskedasticity(timeseries_data):
    """The heteroskedasticity command returns Breusch-Pagan and White results."""
    params = diagnostics.HeteroskedasticityQueryParams(
        data=timeseries_data, y_column="close", x_columns=X_COLUMNS
    )
    assert params.robust is True
    out = diagnostics.heteroskedasticity(params)
    dumped = out.results.model_dump()
    for prefix in ("breusch_pagan", "white"):
        assert 0.0 <= dumped[f"{prefix}_lm_p_value"] <= 1.0
        assert 0.0 <= dumped[f"{prefix}_f_p_value"] <= 1.0
        assert isinstance(dumped[f"{prefix}_lm_statistic"], float)
        assert isinstance(dumped[f"{prefix}_f_statistic"], float)


def test_heteroskedasticity_non_robust(timeseries_data):
    """The heteroskedasticity command accepts the non-robust Breusch-Pagan variant."""
    out = diagnostics.heteroskedasticity(
        diagnostics.HeteroskedasticityQueryParams(
            data=timeseries_data,
            y_column="close",
            x_columns=X_COLUMNS,
            robust=False,
        )
    )
    dumped = out.results.model_dump()
    assert 0.0 <= dumped["breusch_pagan_lm_p_value"] <= 1.0


def test_normality(timeseries_data):
    """The Jarque-Bera normality test returns a statistic and p-value."""
    out = diagnostics.normality(
        diagnostics.NormalityQueryParams(
            data=timeseries_data, y_column="close", x_columns=X_COLUMNS
        )
    )
    dumped = out.results.model_dump()
    assert dumped["jarque_bera"] >= 0.0
    assert 0.0 <= dumped["p_value"] <= 1.0
    assert isinstance(dumped["skew"], float)
    assert isinstance(dumped["kurtosis"], float)


def test_variance_inflation_factor_with_columns(timeseries_data):
    """VIF with an explicit ``columns`` list returns one row per requested column."""
    out = diagnostics.variance_inflation_factor(
        diagnostics.VarianceInflationFactorQueryParams(
            data=timeseries_data, columns=X_COLUMNS
        )
    )
    results = out.results
    assert {row.variable for row in results} == set(X_COLUMNS)
    for row in results:
        assert row.model_dump()["vif"] > 0.0


def test_variance_inflation_factor_without_columns(timeseries_data):
    """Without ``columns`` VIF uses every numeric column in the dataset."""
    params = diagnostics.VarianceInflationFactorQueryParams(data=timeseries_data)
    assert params.columns is None
    out = diagnostics.variance_inflation_factor(params)
    # open/high/low/close/volume.
    assert len(out.results) == 5
    assert {row.variable for row in out.results} == {
        "open",
        "high",
        "low",
        "close",
        "volume",
    }
