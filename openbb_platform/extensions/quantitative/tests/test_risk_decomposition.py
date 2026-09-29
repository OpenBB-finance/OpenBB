"""Tests for ``openbb_quantitative.risk_decomposition``."""

import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_quantitative import risk_decomposition as rd_module


def _params(target_data, factor_data, **kwargs):
    return rd_module.RiskDecompositionQueryParams(
        data=target_data, factors_data=factor_data, target="close", **kwargs
    )


def test_risk_decomposition_happy_path(target_returns_data, factor_matrix_data):
    """Returns rows for every factor plus a Residual row per period."""
    out = rd_module.risk_decomposition(_params(target_returns_data, factor_matrix_data))
    results = out.results
    assert isinstance(results, list)
    assert results

    periods = {r.period for r in results}
    for period in periods:
        period_factors = [r.factor for r in results if r.period == period]
        # f1, f2, rf, Residual
        assert set(period_factors) == {"f1", "f2", "rf", "Residual"}


def test_risk_decomposition_shares_sum_to_one(target_returns_data, factor_matrix_data):
    """Per-period shares sum to 1.0 within floating-point tolerance."""
    out = rd_module.risk_decomposition(
        _params(target_returns_data, factor_matrix_data, risk_free_column="rf")
    )
    df = pd.DataFrame([r.model_dump() for r in out.results])
    sums = df.groupby("period")["share"].sum()
    for period_sum in sums:
        assert period_sum == pytest.approx(1.0, abs=1e-9)


def test_risk_decomposition_with_risk_free(target_returns_data, factor_matrix_data):
    """The risk-free column is dropped from the factor list when provided."""
    out = rd_module.risk_decomposition(
        _params(target_returns_data, factor_matrix_data, risk_free_column="rf")
    )
    factors = {r.factor for r in out.results}
    assert "rf" not in factors
    assert {"f1", "f2", "Residual"}.issubset(factors)


def test_risk_decomposition_constant_target_skipped(
    factor_matrix_df, factor_matrix_data
):
    """Periods where Var(target) is zero are skipped, not divided by zero."""
    constant_target = df_to_basemodel(
        pd.DataFrame(
            {"date": factor_matrix_df["date"], "close": [1.0] * len(factor_matrix_df)}
        )
    )
    out = rd_module.risk_decomposition(
        _params(constant_target, factor_matrix_data, periods=["Max"])
    )
    assert out.results == []


def test_risk_decomposition_skips_too_short_window(
    factor_matrix_df, factor_matrix_data
):
    """Windows with too few observations for OLS are skipped cleanly."""
    short_dates = factor_matrix_df["date"].iloc[:2]
    short_target = df_to_basemodel(
        pd.DataFrame({"date": short_dates, "close": [0.01, -0.005]})
    )
    out = rd_module.risk_decomposition(
        _params(short_target, factor_matrix_data, periods=["Max"])
    )
    assert out.results == []


def test_risk_decomposition_default_periods():
    """The default ``periods`` value enumerates the six named look-back windows."""
    params = rd_module.RiskDecompositionQueryParams(
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
