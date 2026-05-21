"""Tests for ``openbb_quantitative.factors``."""

from math import isfinite

import pandas as pd
import statsmodels.api as sm
from openbb_core.app.utils import df_to_basemodel

from openbb_quantitative import factors as factors_module


def _params(target_data, factor_data, **kwargs):
    return factors_module.FactorRegressionQueryParams(
        data=target_data, factors_data=factor_data, target="close", **kwargs
    )


def test_factors_happy_path(target_returns_data, factor_matrix_data):
    """Returns one row per (period, regressor) with finite stats."""
    out = factors_module.factors(_params(target_returns_data, factor_matrix_data))
    results = out.results
    assert isinstance(results, list)
    assert results

    n_regressors = 4  # const + f1 + f2 + rf
    n_periods = len(set(r.period for r in results))
    assert len(results) == n_periods * n_regressors

    for row in results:
        assert isinstance(row, factors_module.FactorRegressionData)
        for field in ("coefficient", "p_value", "lower_ci", "upper_ci", "r_squared"):
            value = getattr(row, field)
            assert isinstance(value, float)
            assert isfinite(value)


def test_factors_max_window_matches_statsmodels(
    target_returns_df, factor_matrix_df, target_returns_data, factor_matrix_data
):
    """The Max-period coefficients match a direct statsmodels OLS fit."""
    out = factors_module.factors(
        _params(target_returns_data, factor_matrix_data, risk_free_column="rf")
    )
    df = pd.DataFrame([r.model_dump() for r in out.results])
    max_rows = df[df.period == "Max"].set_index("factor")

    aligned = factor_matrix_df.set_index("date").drop(columns=["rf"]).astype(float)
    target = target_returns_df.set_index("date")["close"].astype(
        float
    ) - factor_matrix_df.set_index("date")["rf"].astype(float)
    x = sm.add_constant(aligned)
    model = sm.OLS(target, x).fit()

    for name in model.params.index:
        assert max_rows.loc[name, "coefficient"] == pytest.approx(  # type: ignore[name-defined]
            float(model.params[name]), abs=1e-9
        )


def test_factors_with_risk_free(target_returns_data, factor_matrix_data):
    """When ``risk_free_column`` is set the rf column drops out of the regressors."""
    out = factors_module.factors(
        _params(target_returns_data, factor_matrix_data, risk_free_column="rf")
    )
    factor_names = {r.factor for r in out.results}
    assert "rf" not in factor_names
    assert factor_names == {"const", "f1", "f2"}


def test_factors_specific_periods(target_returns_data, factor_matrix_data):
    """The ``periods`` parameter restricts which look-back windows are returned."""
    out = factors_module.factors(
        _params(target_returns_data, factor_matrix_data, periods=["Max"])
    )
    assert {r.period for r in out.results} == {"Max"}


def test_factors_skips_too_short_windows(factor_matrix_df, factor_matrix_data):
    """Periods whose slice contains fewer obs than regressors+1 are skipped."""
    # Build a target whose factor overlap is two days of business activity.
    short_dates = factor_matrix_df["date"].iloc[:2]
    short_target = df_to_basemodel(
        pd.DataFrame({"date": short_dates, "close": [0.01, -0.005]})
    )
    out = factors_module.factors(
        _params(short_target, factor_matrix_data, periods=["1 Month", "Max"])
    )
    # 2 observations cannot fit a 4-regressor model -> both periods are skipped.
    assert out.results == []


def test_factors_default_periods():
    """The default ``periods`` value enumerates the six named look-back windows."""
    params = factors_module.FactorRegressionQueryParams(
        data=[], factors_data=[], target="close"
    )
    assert params.periods == [
        "1 Month",
        "3 Month",
        "YTD",
        "1 Year",
        "3 Year",
        "Max",
    ]


# pytest is imported here (not at the top) so the local _params helper above
# can reference it without surfacing in autocompletion.
import pytest  # noqa: E402
