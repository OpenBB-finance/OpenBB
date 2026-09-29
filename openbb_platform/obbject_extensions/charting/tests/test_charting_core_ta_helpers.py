"""Test the charting core ta helpers."""

import pandas as pd
import pytest

from openbb_charting.core.plotly_ta.ta_helpers import (
    check_columns,
)


class TestCheckColumns:
    """Tests for the ``check_columns`` helper."""

    def test_check_columns(self):
        """It returns the standard 'close' column when present."""
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
        assert result == "close"

    def test_check_columns_fail(self):
        """It raises IndexError when no close-like column exists."""
        data = pd.DataFrame(
            {
                "open": [1, 2, 3, 4, 5],
                "volume": [1, 2, 3, 4, 5],
            }
        )
        with pytest.raises(IndexError):
            check_columns(data)

    def test_check_columns_non_standard_close(self):
        """It returns a non-standard close column when 'close' is absent."""
        data = pd.DataFrame(
            {
                "High": [1, 2, 3, 4, 5],
                "Low": [1, 2, 3, 4, 5],
                "Adj Close": [1, 2, 3, 4, 5],
            }
        )
        result = check_columns(data)
        assert result == "Adj Close"

    def test_check_columns_prefers_standard_close(self):
        """It prefers the lowercase 'close' over other close-like columns."""
        data = pd.DataFrame(
            {
                "High": [1, 2, 3, 4, 5],
                "Low": [1, 2, 3, 4, 5],
                "Adj Close": [1, 2, 3, 4, 5],
                "close": [1, 2, 3, 4, 5],
            }
        )
        result = check_columns(data)
        assert result == "close"
