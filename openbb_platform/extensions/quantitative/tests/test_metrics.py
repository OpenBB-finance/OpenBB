"""Tests for ``openbb_quantitative.metrics`` - quantitative analysis commands."""

import numpy as np
import pandas as pd
import pytest

from openbb_quantitative import metrics


def test_normality(prices_data):
    """Normality returns finite test statistics and p-values for every test."""
    out = metrics.normality(
        metrics.NormalityQueryParams(data=prices_data, target="close")
    )
    dumped = out.results.model_dump()
    for field in metrics.NormalityQueryParams.__output_columns__:
        value = dumped[field]
        assert isinstance(value, float)
        assert np.isfinite(value)


def test_normality_non_numeric_raises():
    """A non-numeric target column raises a clear ValueError."""
    data = [{"close": "a"}, {"close": "b"}, {"close": "c"}]
    params = metrics.NormalityQueryParams(data=data, target="close")
    with pytest.raises(ValueError, match="must be numeric"):
        metrics.normality(params)


def test_capm(prices_data, monkeypatch):
    """CAPM reports finite risk measures from mocked monthly Fama-French factors."""

    def fake(start_date, end_date):
        rng = np.random.default_rng(0)
        index = pd.date_range(start_date, end_date, freq="MS")
        return pd.DataFrame(
            {
                "mkt_rf": rng.normal(0.01, 0.04, len(index)),
                "smb": rng.normal(0.0, 0.02, len(index)),
                "hml": rng.normal(0.0, 0.02, len(index)),
                "rf": rng.normal(0.002, 0.001, len(index)),
            },
            index=index,
        )

    monkeypatch.setattr("openbb_quantitative.helpers.get_fama_raw", fake)
    out = metrics.capm(metrics.CapmQueryParams(data=prices_data, target="close"))
    dumped = out.results.model_dump()
    for field in metrics.CapmQueryParams.__output_columns__:
        value = dumped[field]
        assert isinstance(value, float)
        assert np.isfinite(value)


def test_unitroot_test(prices_data):
    """The unit root test reports finite ADF and KPSS statistics."""
    out = metrics.unitroot_test(
        metrics.UnitRootTestQueryParams(data=prices_data, target="close")
    )
    params = metrics.UnitRootTestQueryParams(data=prices_data, target="close")
    assert params.fuller_reg == "c"
    assert params.kpss_reg == "c"
    assert params.maxlag is None
    assert params.autolag == "AIC"
    assert params.nlags == "auto"
    dumped = out.results.model_dump()
    assert isinstance(dumped["adf_statistic"], float)
    assert np.isfinite(dumped["adf_statistic"])
    assert isinstance(dumped["adf_p_value"], float)
    assert isinstance(dumped["adf_nlags"], int)
    assert isinstance(dumped["adf_nobs"], int)
    assert isinstance(dumped["adf_icbest"], float)
    assert isinstance(dumped["kpss_statistic"], float)
    assert isinstance(dumped["kpss_p_value"], float)
    assert isinstance(dumped["kpss_nlags"], int)
    assert isinstance(dumped["kpss_p_value_interpolated"], bool)


def test_unitroot_test_regression_options(prices_data):
    """The unit root test accepts non-default ADF and KPSS regression terms."""
    out = metrics.unitroot_test(
        metrics.UnitRootTestQueryParams(
            data=prices_data,
            target="close",
            fuller_reg="ct",
            kpss_reg="ct",
        )
    )
    dumped = out.results.model_dump()
    assert np.isfinite(dumped["adf_statistic"])
    assert np.isfinite(dumped["kpss_statistic"])


def test_unitroot_test_no_autolag(prices_data):
    """With autolag disabled the ADF test uses maxlag directly and has no icbest."""
    out = metrics.unitroot_test(
        metrics.UnitRootTestQueryParams(
            data=prices_data, target="close", maxlag=4, autolag=None
        )
    )
    dumped = out.results.model_dump()
    assert dumped["adf_nlags"] == 4
    assert dumped["adf_icbest"] is None


def test_unitroot_test_explicit_kpss_nlags(prices_data):
    """The KPSS test accepts an explicit integer lag count."""
    out = metrics.unitroot_test(
        metrics.UnitRootTestQueryParams(data=prices_data, target="close", nlags=6)
    )
    assert out.results.kpss_nlags == 6


def test_summary(prices_data):
    """Summary reports finite descriptive statistics for the target column."""
    out = metrics.summary(metrics.SummaryQueryParams(data=prices_data, target="close"))
    dumped = out.results.model_dump()
    assert isinstance(dumped["count"], int)
    assert dumped["count"] == 250
    for field in ("mean", "std", "var", "min", "p25", "p50", "p75", "max"):
        value = dumped[field]
        assert isinstance(value, float)
        assert np.isfinite(value)
    assert dumped["min"] <= dumped["p25"] <= dumped["p50"] <= dumped["p75"]
    assert dumped["p75"] <= dumped["max"]
