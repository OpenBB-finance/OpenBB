"""Tests for quantitative router commands."""

from math import sin

import pytest
from openbb_core.provider.abstract.data import Data
from openbb_quantitative.quantitative_router import normality, summary, unitroot_test


def test_normality_returns_all_test_results():
    """Normality should return statistics and probabilities for every test."""
    data = [Data(close=value) for value in [1.2, 2.1, 2.9, 4.2, 5.1, 5.8, 7.3, 7.9]]

    result = normality(data, "close").results

    for test_result in [
        result.kurtosis,
        result.skewness,
        result.jarque_bera,
        result.shapiro_wilk,
        result.kolmogorov_smirnov,
    ]:
        assert test_result.statistic is not None
        assert 0 <= test_result.p_value <= 1


def test_unitroot_returns_adf_and_kpss_results():
    """Unit-root analysis should return populated ADF and KPSS summaries."""
    data = [Data(close=0.01 * index + sin(index / 3)) for index in range(60)]

    result = unitroot_test(data, "close").results

    assert result.adf.nobs > 0
    assert result.adf.nlags >= 0
    assert 0 <= result.adf.p_value <= 1
    assert result.kpss.nlags >= 0
    assert 0 <= result.kpss.p_value <= 1


def test_summary_returns_descriptive_statistics():
    """Summary should calculate the documented descriptive statistics."""
    data = [Data(close=float(value)) for value in range(1, 11)]

    result = summary(data, "close").results

    assert result.count == 10
    assert result.mean == pytest.approx(5.5)
    assert result.var == pytest.approx(result.std**2)
    assert result.min == 1
    assert result.p_25 == pytest.approx(3.25)
    assert result.p_50 == pytest.approx(5.5)
    assert result.p_75 == pytest.approx(7.75)
    assert result.max == 10