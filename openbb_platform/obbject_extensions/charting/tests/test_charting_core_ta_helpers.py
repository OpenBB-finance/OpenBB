"""Test the charting core ta helpers."""

import pandas as pd
import pytest
from openbb_charting.core.plotly_ta.ta_helpers import (
    check_columns,
)


def test_check_columns():
    """Test check_columns."""
    data = pd.DataFrame(
        {
            "open": [1, 2, 3, 4, 5],
            "high": [1, 2, 3, 4, 5],
            "low": [1, 2, 3, 4, 5],
            "close": [1, 2, 3, 4, 5],
            "volume": [1, 2, 3, 4, 5],
        }
    )
    result = check_columns(data)
    assert result


def test_check_columns_fail():
    """Test check_columns."""
    data = pd.DataFrame(
        {
            "open": [1, 2, 3, 4, 5],
            "volume": [1, 2, 3, 4, 5],
        }
    )
    with pytest.raises(IndexError):
        check_columns(data)
