import numpy as np
import pandas as pd
import pytest
from statsmodels.stats.diagnostic import lilliefors

from openbb_quantitative import metrics, stats

MONTH_STARTS = pd.date_range("2023-02-01", periods=7, freq="MS")
MONTH_ENDS = MONTH_STARTS - pd.Timedelta(days=1)


def _month_end_prices(market_excess, risk_free, alpha=0.002, beta=1.5):
    prices = [100.0]
    for market, rf in zip(market_excess, risk_free):
        prices.append(prices[-1] * (1 + rf + alpha + beta * market))
    return [
        {"date": day.date(), "close": price} for day, price in zip(MONTH_ENDS, prices)
    ]


def _factors(market_excess, risk_free, index):
    return pd.DataFrame(
        {"mkt_rf": market_excess, "smb": 0.0, "hml": 0.0, "rf": risk_free},
        index=index,
    )


def test_normality(prices_data):
    out = metrics.normality(
        metrics.NormalityQueryParams(data=prices_data, target="close")
    )
    dumped = out.results.model_dump()
    for field in metrics.NormalityQueryParams.__output_columns__:
        value = dumped[field]
        assert isinstance(value, float)
        assert np.isfinite(value)


def test_normality_non_numeric_raises():
    data = [{"close": "a"}, {"close": "b"}, {"close": "c"}]
    params = metrics.NormalityQueryParams(data=data, target="close")
    with pytest.raises(ValueError, match="must be numeric"):
        metrics.normality(params)


def test_capm(prices_data, monkeypatch):
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


def test_capm_recovers_known_beta(monkeypatch):
    market_excess = [-0.03, -0.01, 0.01, 0.02, 0.04, -0.02]
    risk_free = [0.001, 0.002, 0.001, 0.003, 0.002, 0.001]
    factors = _factors(market_excess, risk_free, MONTH_STARTS[:6])
    monkeypatch.setattr(
        "openbb_quantitative.helpers.get_fama_raw", lambda start, end: factors
    )
    out = metrics.capm(
        metrics.CapmQueryParams(
            data=_month_end_prices(market_excess, risk_free), target="close"
        )
    ).results
    assert out.market_risk == pytest.approx(1.5)
    assert out.systematic_risk == pytest.approx(1.0)
    assert out.idiosyncratic_risk == pytest.approx(0.0, abs=1e-9)


def test_capm_single_month_of_daily_prices_raises():
    days = pd.bdate_range("2023-03-01", "2023-03-31")
    data = [{"date": day.date(), "close": 100.0 + i} for i, day in enumerate(days)]
    with pytest.raises(
        ValueError, match="at least 3 monthly returns; the data produced 0"
    ):
        metrics.capm(metrics.CapmQueryParams(data=data, target="close"))


def test_capm_two_monthly_returns_raises():
    data = _month_end_prices([0.01, 0.02], [0.001, 0.001])
    with pytest.raises(
        ValueError, match="at least 3 monthly returns; the data produced 2"
    ):
        metrics.capm(metrics.CapmQueryParams(data=data, target="close"))


def test_capm_insufficient_factor_overlap_raises(monkeypatch):
    market_excess = [-0.03, -0.01, 0.01, 0.02, 0.04, -0.02]
    risk_free = [0.001] * 6
    factors = _factors([0.01, 0.02], [0.001, 0.001], MONTH_STARTS[:2])
    monkeypatch.setattr(
        "openbb_quantitative.helpers.get_fama_raw", lambda start, end: factors
    )
    with pytest.raises(
        ValueError, match="overlapping the Fama-French factors; found 2"
    ):
        metrics.capm(
            metrics.CapmQueryParams(
                data=_month_end_prices(market_excess, risk_free), target="close"
            )
        )


def test_normality_kolmogorov_smirnov_uses_sample_moments():
    sample = np.random.default_rng(3).normal(100.0, 2.0, 400)
    data = [{"close": float(value)} for value in sample]
    out = metrics.normality(
        metrics.NormalityQueryParams(data=data, target="close")
    ).results
    statistic, p_value = lilliefors(sample, dist="norm")
    assert out.kolmogorov_smirnov_statistic == pytest.approx(statistic)
    assert out.kolmogorov_smirnov_p_value == pytest.approx(p_value)
    assert out.kolmogorov_smirnov_p_value > 0.05


def test_normality_kolmogorov_smirnov_rejects_heavy_tails():
    sample = np.random.default_rng(3).standard_t(2, 400)
    data = [{"close": float(value)} for value in sample]
    out = metrics.normality(
        metrics.NormalityQueryParams(data=data, target="close")
    ).results
    assert out.kolmogorov_smirnov_p_value < 0.05


def test_stats_dispersion_matches_summary():
    data = [{"close": float(value)} for value in [1, 2, 3, 4, 5]]
    summary = metrics.summary(metrics.SummaryQueryParams(data=data, target="close"))
    stdev = stats.stdev(stats.StatsStdevQueryParams(data=data, target="close"))
    variance = stats.variance(stats.StatsVarianceQueryParams(data=data, target="close"))
    assert stdev.results.stdev == pytest.approx(summary.results.std)
    assert variance.results.variance == pytest.approx(summary.results.var)
    assert summary.results.var == pytest.approx(2.5)


def test_unitroot_test(prices_data):
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
    out = metrics.unitroot_test(
        metrics.UnitRootTestQueryParams(
            data=prices_data, target="close", maxlag=4, autolag=None
        )
    )
    dumped = out.results.model_dump()
    assert dumped["adf_nlags"] == 4
    assert dumped["adf_icbest"] is None


def test_unitroot_test_explicit_kpss_nlags(prices_data):
    out = metrics.unitroot_test(
        metrics.UnitRootTestQueryParams(data=prices_data, target="close", nlags=6)
    )
    assert out.results.kpss_nlags == 6


def test_summary(prices_data):
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
