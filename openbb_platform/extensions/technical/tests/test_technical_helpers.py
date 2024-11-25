"""Test the technical helpers module."""

import numpy as np
import pandas as pd
import pytest
from extensions.technical.openbb_technical.helpers import (
    calculate_cones,
    calculate_fib_levels,
    clenow_momentum,
    garman_klass,
    hodges_tompkins,
    parkinson,
    rogers_satchell,
    validate_data,
    yang_zhang,
)

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="module")
def mock_data(top_range: int = 100):
    """Mock data for testing."""
    _open = pd.Series(np.arange(1, top_range))
    _high = pd.Series(np.arange(1, top_range))
    _low = pd.Series(np.arange(1, top_range))
    _close = pd.Series(np.arange(1, top_range))
    _volume = pd.Series(np.arange(1, top_range))
    _date = pd.Series(pd.date_range("2021-01-01", periods=top_range - 1, freq="D"))
    return pd.DataFrame(
        {
            "open": _open,
            "high": _high,
            "low": _low,
            "close": _close,
            "volume": _volume,
            "date": _date,
        }
    ).set_index("date")


def test_parkinson_with_mock_data(mock_data):
    """Test parkinson with valid input."""
    result = parkinson(mock_data)
    assert not result.empty


def test_garman_klass_with_mock_data(mock_data):
    """Test garman_klass with valid input."""
    result = garman_klass(mock_data)
    assert not result.empty


def test_hodges_tompkins_with_mock_data(mock_data):
    """Test hodges_tompkins with valid input."""
    result = hodges_tompkins(mock_data)
    assert not result.empty


def test_rogers_satchell_with_mock_data(mock_data):
    """Test rogers_satchell with valid input."""
    result = rogers_satchell(mock_data)
    assert not result.empty


def test_yang_zhang_with_mock_data(mock_data):
    """Test yang_zhang with valid input."""
    result = yang_zhang(mock_data)
    assert not result.empty


def test_clenow_momentum_with_mock_data(mock_data):
    """Test clenow_momentum with valid input."""
    result = clenow_momentum(mock_data["close"])
    assert result


def test_calculate_cones_with_mock_data(mock_data):
    """Test calculate_cones with valid input."""
    result = calculate_cones(
        mock_data,
        lower_q=0.1,
        upper_q=0.9,
        is_crypto=False,
        model="std",
    )
    assert not result.empty


def test_calculate_fib_levels_with_mock_data(mock_data):
    """Test calculate_fib_levels with valid input."""
    result = calculate_fib_levels(mock_data, "close")
    assert result


def test_validate_data_with_mock_data(mock_data):
    """Test validate_data with valid input."""
    try:
        validate_data(mock_data["close"].tolist(), 20)
    except ValueError:
        pytest.fail("validate_data raised ValueError unexpectedly!")
