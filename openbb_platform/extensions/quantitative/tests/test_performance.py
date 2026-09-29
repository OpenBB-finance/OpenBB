from math import isfinite, isnan, sqrt

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_quantitative import performance

PERIODS_PER_YEAR = 252


def _returns(prices_df):
    closes = pd.Series(
        prices_df["close"].to_numpy(), index=pd.to_datetime(prices_df["date"])
    )
    return closes.pct_change().dropna()


def _returns_data(prices_df):
    return [
        {"date": day.date(), "return": float(value)}
        for day, value in _returns(prices_df).items()
    ]


def test_query_params_defaults():
    omega = performance.OmegaRatioQueryParams(data=[], target="return")
    assert omega.threshold_start == 0.0
    assert omega.threshold_end == 1.5
    assert omega.bins == 50

    sharpe = performance.SharpeRatioQueryParams(data=[], target="close")
    assert sharpe.rfr == 0.0
    assert sharpe.window == 252
    assert sharpe.index == "date"

    sortino = performance.SortinoRatioQueryParams(data=[], target="close")
    assert sortino.target_return == 0.0
    assert sortino.window == 252
    assert sortino.adjusted is False
    assert sortino.index == "date"


def test_omega_ratio(prices_df):
    params = performance.OmegaRatioQueryParams(
        data=_returns_data(prices_df), target="return"
    )
    results = performance.omega_ratio(params).results
    assert isinstance(results, list)
    assert len(results) == 50
    for row in results:
        assert isinstance(row, performance.OmegaRatioData)
        assert isfinite(row.threshold)
        assert isfinite(row.omega)


def test_omega_ratio_bins(prices_df):
    out = performance.omega_ratio(
        performance.OmegaRatioQueryParams(
            data=_returns_data(prices_df), target="return", bins=10
        )
    )
    assert len(out.results) == 10


def test_omega_ratio_uses_per_period_threshold(prices_df):
    out = performance.omega_ratio(
        performance.OmegaRatioQueryParams(
            data=_returns_data(prices_df),
            target="return",
            threshold_start=0.1,
            threshold_end=0.1,
            bins=1,
        )
    ).results
    excess = _returns(prices_df) - (1.1 ** (1 / PERIODS_PER_YEAR) - 1)
    expected = excess[excess > 0].sum() / (-excess[excess < 0].sum() + 1e-6)
    assert out[0].threshold == pytest.approx(0.1)
    assert out[0].omega == pytest.approx(expected)


def test_sharpe_ratio(prices_data):
    params = performance.SharpeRatioQueryParams(
        data=prices_data, target="close", window=20
    )
    results = performance.sharpe_ratio(params).results
    assert isinstance(results, list)
    assert len(results) > 0
    for row in results:
        assert isinstance(row, performance.SharpeRatioData)
        assert row.date is not None
        assert isfinite(row.sharpe_ratio)


def test_sharpe_ratio_matches_annualized_formula(prices_data, prices_df):
    rfr = 0.03
    results = performance.sharpe_ratio(
        performance.SharpeRatioQueryParams(
            data=prices_data, target="close", window=60, rfr=rfr
        )
    ).results
    returns = _returns(prices_df)
    window = returns.iloc[-60:]
    period_rfr = (1 + rfr) ** (1 / PERIODS_PER_YEAR) - 1
    expected = (window.mean() - period_rfr) / window.std() * sqrt(PERIODS_PER_YEAR)
    assert len(results) == len(returns) - 60 + 1
    assert results[-1].sharpe_ratio == pytest.approx(expected)


def test_sharpe_ratio_is_invariant_to_price_scale(prices_df):
    base = performance.sharpe_ratio(
        performance.SharpeRatioQueryParams(
            data=df_to_basemodel(prices_df), target="close", window=60
        )
    ).results
    scaled = performance.sharpe_ratio(
        performance.SharpeRatioQueryParams(
            data=df_to_basemodel(prices_df.assign(close=prices_df["close"] * 10)),
            target="close",
            window=60,
        )
    ).results
    assert [row.sharpe_ratio for row in scaled] == pytest.approx(
        [row.sharpe_ratio for row in base]
    )


def test_sharpe_ratio_window_longer_than_returns_raises(prices_data):
    with pytest.raises(ValueError, match="larger than the data length '249'"):
        performance.sharpe_ratio(
            performance.SharpeRatioQueryParams(
                data=prices_data, target="close", window=250
            )
        )


def test_sharpe_ratio_drops_undefined_values(prices_df):
    flat = df_to_basemodel(prices_df.assign(close=100.0))
    results = performance.sharpe_ratio(
        performance.SharpeRatioQueryParams(data=flat, target="close", window=20)
    ).results
    assert results == []


def test_sortino_ratio(prices_data):
    params = performance.SortinoRatioQueryParams(
        data=prices_data, target="close", window=20
    )
    results = performance.sortino_ratio(params).results
    assert isinstance(results, list)
    assert len(results) > 0
    for row in results:
        assert isinstance(row, performance.SortinoRatioData)
        assert row.date is not None
        assert isfinite(row.sortino_ratio)


def test_sortino_ratio_matches_downside_deviation_formula(prices_data, prices_df):
    target_return = 0.02
    results = performance.sortino_ratio(
        performance.SortinoRatioQueryParams(
            data=prices_data, target="close", window=60, target_return=target_return
        )
    ).results
    returns = _returns(prices_df)
    period_target = (1 + target_return) ** (1 / PERIODS_PER_YEAR) - 1
    excess = returns.iloc[-60:].to_numpy() - period_target
    downside = np.sqrt(np.mean(np.minimum(excess, 0.0) ** 2))
    expected = excess.mean() / downside * sqrt(PERIODS_PER_YEAR)
    assert len(results) == len(returns) - 60 + 1
    assert results[-1].sortino_ratio == pytest.approx(expected)


def test_sortino_ratio_drops_undefined_values(prices_df):
    flat = df_to_basemodel(prices_df.assign(close=100.0))
    results = performance.sortino_ratio(
        performance.SortinoRatioQueryParams(data=flat, target="close", window=20)
    ).results
    assert results == []


def test_sortino_ratio_adjusted(prices_data):
    unadjusted = performance.sortino_ratio(
        performance.SortinoRatioQueryParams(
            data=prices_data, target="close", window=20, adjusted=False
        )
    ).results
    adjusted = performance.sortino_ratio(
        performance.SortinoRatioQueryParams(
            data=prices_data, target="close", window=20, adjusted=True
        )
    ).results
    assert len(adjusted) == len(unadjusted)
    assert len(adjusted) > 0
    for adj, unadj in zip(adjusted, unadjusted):
        assert not isnan(adj.sortino_ratio)
        assert adj.sortino_ratio == unadj.sortino_ratio / sqrt(2)
