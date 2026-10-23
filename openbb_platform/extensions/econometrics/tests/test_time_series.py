"""Tests for ``openbb_econometrics.time_series`` - stationarity and volatility."""

import pytest

from openbb_econometrics import time_series


@pytest.mark.parametrize("regression", ["c", "ct", "ctt"])
def test_unit_root(timeseries_data, regression):
    """The ADF unit-root test returns a statistic and critical values."""
    out = time_series.unit_root(
        time_series.UnitRootQueryParams(
            data=timeseries_data, column="close", regression=regression
        )
    )
    dumped = out.results.model_dump()
    assert isinstance(dumped["adf_stat"], float)
    assert 0.0 <= dumped["p_value"] <= 1.0
    assert dumped["used_lag"] >= 0
    assert dumped["nobs"] > 0
    assert isinstance(dumped["ic_best"], float)
    assert set(dumped["critical_values"]) == {"1%", "5%", "10%"}


def test_unit_root_defaults(timeseries_data):
    """The ADF parameters default to a constant regression with AIC lag selection."""
    params = time_series.UnitRootQueryParams(data=timeseries_data, column="close")
    assert params.regression == "c"
    assert params.maxlag is None
    assert params.autolag == "AIC"


def test_unit_root_no_autolag(timeseries_data):
    """With ``autolag`` disabled the ADF test uses ``maxlag`` directly."""
    out = time_series.unit_root(
        time_series.UnitRootQueryParams(
            data=timeseries_data, column="close", maxlag=4, autolag=None
        )
    )
    dumped = out.results.model_dump()
    assert dumped["used_lag"] == 4
    assert dumped["ic_best"] is None


@pytest.mark.parametrize("regression", ["c", "ct"])
def test_kpss(timeseries_data, regression):
    """The KPSS stationarity test returns a statistic and critical values."""
    out = time_series.kpss(
        time_series.KpssQueryParams(
            data=timeseries_data, column="close", regression=regression
        )
    )
    dumped = out.results.model_dump()
    assert isinstance(dumped["kpss_stat"], float)
    assert 0.0 <= dumped["p_value"] <= 1.0
    assert dumped["lags"] >= 0
    assert dumped["critical_values"]
    assert isinstance(dumped["p_value_interpolated"], bool)
    assert dumped["p_value_interpolated"] == (0.01 < dumped["p_value"] < 0.1)


def test_kpss_defaults(timeseries_data):
    """The KPSS parameters default to a constant regression and automatic lags."""
    params = time_series.KpssQueryParams(data=timeseries_data, column="close")
    assert params.regression == "c"
    assert params.nlags == "auto"


@pytest.mark.parametrize("nlags", ["auto", "legacy", 5])
def test_kpss_nlags(timeseries_data, nlags):
    """The KPSS test accepts automatic, legacy, and explicit integer lag settings."""
    out = time_series.kpss(
        time_series.KpssQueryParams(data=timeseries_data, column="close", nlags=nlags)
    )
    dumped = out.results.model_dump()
    assert dumped["kpss_stat"] >= 0.0
    assert dumped["lags"] >= 0


def test_cointegration(timeseries_data):
    """Engle-Granger cointegration returns one row per column pair."""
    out = time_series.cointegration(
        time_series.CointegrationQueryParams(
            data=timeseries_data, columns=["open", "high", "close"]
        )
    )
    results = out.results
    # 3 columns -> 3 pairwise combinations.
    assert len(results) == 3
    pairs = {row.pair for row in results}
    assert pairs == {"open/high", "open/close", "high/close"}
    for row in results:
        dumped = row.model_dump()
        assert isinstance(dumped["c"], float)
        assert isinstance(dumped["gamma"], float)
        assert isinstance(dumped["alpha"], float)
        assert isinstance(dumped["adf_stat"], float)


@pytest.mark.parametrize("deterministic_order", [-1, 0, 1])
def test_cointegration_johansen(timeseries_data, deterministic_order):
    """The Johansen test returns one row per cointegration rank hypothesis."""
    out = time_series.cointegration_johansen(
        time_series.CointegrationJohansenQueryParams(
            data=timeseries_data,
            columns=["open", "close"],
            deterministic_order=deterministic_order,
        )
    )
    results = out.results
    # Two series -> two rank hypotheses.
    assert len(results) == 2
    for rank, row in enumerate(results):
        dumped = row.model_dump()
        assert dumped["rank"] == rank
        assert isinstance(dumped["eigenvalue"], float)
        assert isinstance(dumped["trace_statistic"], float)
        assert isinstance(dumped["max_eig_statistic"], float)
        assert dumped["trace_crit_90"] <= dumped["trace_crit_99"]


def test_cointegration_johansen_defaults(timeseries_data):
    """The Johansen ``deterministic_order``/``k_ar_diff`` defaults are 0 and 1."""
    params = time_series.CointegrationJohansenQueryParams(
        data=timeseries_data, columns=["open", "close"]
    )
    assert params.deterministic_order == 0
    assert params.k_ar_diff == 1


def test_causality(timeseries_data):
    """The Granger causality test returns one row per Granger sub-test."""
    out = time_series.causality(
        time_series.CausalityQueryParams(
            data=timeseries_data, y_column="close", x_column="open", lag=2
        )
    )
    results = out.results
    assert len(results) > 0
    for row in results:
        dumped = row.model_dump()
        assert dumped["lag"] == 2
        assert isinstance(dumped["test"], str)
        assert isinstance(dumped["statistic"], float)
        assert 0.0 <= dumped["p_value"] <= 1.0


def test_causality_default_lag(timeseries_data):
    """The Granger causality ``lag`` parameter defaults to 3."""
    params = time_series.CausalityQueryParams(
        data=timeseries_data, y_column="close", x_column="open"
    )
    assert params.lag == 3


@pytest.mark.parametrize(
    ("p", "q", "distribution"),
    [
        (1, 1, "normal"),
        (2, 1, "t"),
        (1, 2, "skewt"),
        (2, 2, "ged"),
    ],
)
def test_garch(timeseries_data, p, q, distribution):
    """GARCH returns a conditional-volatility series and fit metadata in ``extra``."""
    out = time_series.garch(
        time_series.GarchQueryParams(
            data=timeseries_data,
            column="close",
            p=p,
            q=q,
            distribution=distribution,
        )
    )
    results = out.results
    assert len(results) == 120
    for index, row in enumerate(results):
        dumped = row.model_dump()
        assert dumped["date"] == index
        assert dumped["conditional_volatility"] > 0.0

    metadata = out.extra["results_metadata"]
    assert set(metadata) == {"params", "aic", "bic", "log_likelihood"}
    assert isinstance(metadata["params"], dict)
    assert isinstance(metadata["aic"], float)
    assert isinstance(metadata["bic"], float)
    assert isinstance(metadata["log_likelihood"], float)


def test_garch_defaults(timeseries_data):
    """The GARCH model-configuration parameters default to a plain GARCH(1, 1)."""
    params = time_series.GarchQueryParams(data=timeseries_data, column="close")
    assert params.mean == "Constant"
    assert params.lags == 0
    assert params.vol == "GARCH"
    assert params.p == 1
    assert params.o == 0
    assert params.q == 1
    assert params.power == 2.0
    assert params.distribution == "normal"
    assert params.x_columns is None


def test_garch_configurable_volatility_model(timeseries_data):
    """garch fits non-default mean and volatility processes."""
    out = time_series.garch(
        time_series.GarchQueryParams(
            data=timeseries_data,
            column="close",
            mean="AR",
            lags=2,
            vol="EGARCH",
            o=1,
        )
    )
    assert out.results
    assert all(row.conditional_volatility > 0.0 for row in out.results)


def test_garch_with_exogenous_regressor(timeseries_data):
    """garch accepts exogenous mean regressors through x_columns."""
    out = time_series.garch(
        time_series.GarchQueryParams(
            data=timeseries_data,
            column="close",
            x_columns=["open"],
            mean="LS",
        )
    )
    assert out.results
    assert all(row.conditional_volatility > 0.0 for row in out.results)


def test_garch_preserves_input_dates():
    """garch reports each observation's input date, not a 0-based position."""
    rows = [
        {
            "date": f"2022-{(i // 28) + 1:02d}-{(i % 28) + 1:02d}",
            "close": 100.0 + (i % 7) - (i % 3) * 1.5 + i * 0.2,
        }
        for i in range(60)
    ]
    out = time_series.garch(time_series.GarchQueryParams(data=rows, column="close"))
    dates = [str(row.model_dump()["date"]) for row in out.results]
    assert len(dates) == 60
    assert dates[0] == "2022-01-01"
    assert dates[-1] == "2022-03-04"
