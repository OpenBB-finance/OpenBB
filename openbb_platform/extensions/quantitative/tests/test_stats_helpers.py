import pandas as pd
import pytest

from openbb_quantitative._stats_helpers import (
    kurtosis_,
    mean_,
    skew_,
    std_dev_,
    var_,
)

test_data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


def test_kurtosis():
    assert kurtosis_(test_data) == pytest.approx(-1.224, abs=1e-3)


def test_skew():
    assert skew_(test_data) == pytest.approx(0.0, abs=1e-3)


def test_std_dev():
    assert std_dev_(test_data) == pytest.approx(test_data.std())
    assert std_dev_(test_data.to_numpy()) == pytest.approx(3.028, abs=1e-3)


def test_mean():
    assert mean_(test_data) == pytest.approx(5.5, abs=1e-3)


def test_var():
    assert var_(test_data) == pytest.approx(test_data.var())
    assert var_(test_data.to_numpy()) == pytest.approx(9.167, abs=1e-3)
