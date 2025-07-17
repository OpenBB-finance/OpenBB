"""Test the econometrics utils module."""

import numpy as np
import pandas as pd
from openbb_econometrics.utils import (
    get_engle_granger_two_step_cointegration_test,
    mock_multi_index_data,
)


def test_get_engle_granger_two_step_cointegration_test():
    """Test the get_engle_granger_two_step_cointegration_test function."""
    x = pd.Series(np.random.randn(100))
    y = pd.Series(np.random.randn(100))

    result = get_engle_granger_two_step_cointegration_test(x, y)

    assert result


def test_mock_multi_index_data():
    """Test the mock_multi_index_data function."""
    mi_data = mock_multi_index_data()
    assert isinstance(mi_data, pd.DataFrame)
    assert mi_data.index.nlevels == 2
