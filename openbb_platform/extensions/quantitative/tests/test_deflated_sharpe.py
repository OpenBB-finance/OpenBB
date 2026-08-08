"""Test the deflated Sharpe ratio helper."""

import math

import pandas as pd
import pytest
from extensions.quantitative.openbb_quantitative.helpers import (
    deflated_sharpe_stats,
)

# Reference values computed with the numguard reference implementation of
# Bailey & Lopez de Prado (2014) on the same deterministic series
# (population moments, null trial dispersion 1/sqrt(n-1)).
RETURNS = pd.Series(
    [0.003 + 0.01 * math.sin(i) + 0.004 * math.cos(3 * i) for i in range(90)]
)


def test_matches_reference_implementation():
    """Parity against the reference implementation."""
    result = deflated_sharpe_stats(RETURNS, trials=50)
    assert result["sharpe"] == pytest.approx(0.4101142526095976, abs=1e-9)
    assert result["expected_max_sharpe"] == pytest.approx(
        0.24128764537744862, abs=1e-9
    )
    assert result["deflated_sharpe_ratio"] == pytest.approx(
        0.9399085246020616, abs=1e-7
    )
    assert result["observations"] == 90
    assert result["trials"] == 50


def test_single_trial_has_no_deflation():
    """With one trial the bar is zero: pure probabilistic Sharpe vs 0."""
    result = deflated_sharpe_stats(RETURNS, trials=1)
    assert result["expected_max_sharpe"] == 0.0
    assert result["deflated_sharpe_ratio"] == pytest.approx(
        0.9999199954582253, abs=1e-7
    )


def test_deflation_is_monotonic_in_trials():
    """More attempts must never make the same result more credible."""
    values = [
        deflated_sharpe_stats(RETURNS, trials=n)["deflated_sharpe_ratio"]
        for n in (1, 10, 100, 1000)
    ]
    assert all(values[i] > values[i + 1] for i in range(len(values) - 1))


def test_invalid_inputs_raise():
    """Trials and sample-size guards."""
    with pytest.raises(ValueError):
        deflated_sharpe_stats(RETURNS, trials=0)
    with pytest.raises(ValueError):
        deflated_sharpe_stats(RETURNS.head(2), trials=10)
    with pytest.raises(ValueError):
        deflated_sharpe_stats(pd.Series([0.01] * 10), trials=10)
