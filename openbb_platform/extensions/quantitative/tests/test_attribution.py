"""Tests for ``openbb_quantitative.attribution``."""

from math import isnan

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_quantitative import attribution as att_module


def _params(target_data, factor_data, **kwargs):
    return att_module.ReturnAttributionQueryParams(
        data=target_data, factors_data=factor_data, target="close", **kwargs
    )


def test_attribution_happy_path(target_returns_data, factor_matrix_data):
    """Returns rows for every regressor plus Alpha and Residual per period."""
    out = att_module.attribution(_params(target_returns_data, factor_matrix_data))
    results = out.results
    assert isinstance(results, list)
    assert results

    periods = {r.period for r in results}
    for period in periods:
        names = [r.factor for r in results if r.period == period]
        # const is hidden behind the Alpha label; rf is in the factor set unless
        # risk_free_column is provided.
        assert set(names) == {"f1", "f2", "rf", "Alpha", "Residual"}


def test_attribution_contributions_sum_to_total(
    target_returns_df, factor_matrix_df, target_returns_data, factor_matrix_data
):
    """Per-period contributions sum to the period's total target return."""
    out = att_module.attribution(
        _params(target_returns_data, factor_matrix_data, risk_free_column="rf")
    )
    df = pd.DataFrame([r.model_dump() for r in out.results])
    sums = df.groupby("period")["contribution"].sum()

    # Recompute the expected per-period target totals (excess of rf).
    target = target_returns_df.set_index("date")["close"].astype(
        float
    ) - factor_matrix_df.set_index("date")["rf"].astype(float)
    max_total = float(target.sum())
    assert sums["Max"] == pytest.approx(max_total, abs=1e-9)


def test_attribution_zero_total_uses_nan_share(factor_matrix_df, factor_matrix_data):
    """When the period's total return is zero, share is NaN (no divide-by-zero)."""
    n = len(factor_matrix_df)
    half = n // 2
    # Alternating +eps / -eps gives an exactly zero sum.
    series = np.tile([1e-6, -1e-6], half + 1)[:n]
    zero_target = df_to_basemodel(
        pd.DataFrame({"date": factor_matrix_df["date"], "close": series})
    )
    out = att_module.attribution(
        _params(zero_target, factor_matrix_data, periods=["Max"])
    )
    shares = [r.share for r in out.results]
    assert shares
    assert all(isnan(s) for s in shares)


def test_attribution_with_risk_free_drops_rf(target_returns_data, factor_matrix_data):
    """The risk-free column is removed from the factor set when provided."""
    out = att_module.attribution(
        _params(target_returns_data, factor_matrix_data, risk_free_column="rf")
    )
    factors = {r.factor for r in out.results}
    assert "rf" not in factors
    assert {"f1", "f2", "Alpha", "Residual"}.issubset(factors)


def test_attribution_skips_too_short_window(factor_matrix_df, factor_matrix_data):
    """Windows with too few observations for OLS are skipped cleanly."""
    short_dates = factor_matrix_df["date"].iloc[:2]
    short_target = df_to_basemodel(
        pd.DataFrame({"date": short_dates, "close": [0.01, -0.005]})
    )
    out = att_module.attribution(
        _params(short_target, factor_matrix_data, periods=["Max"])
    )
    assert out.results == []


def test_attribution_default_periods():
    """The default ``periods`` value enumerates the six named look-back windows."""
    params = att_module.ReturnAttributionQueryParams(
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
