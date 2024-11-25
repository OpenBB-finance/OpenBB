"""Test the quantitative helpers."""

import pandas as pd
from extensions.quantitative.openbb_quantitative.helpers import (
    validate_window,
)


def test_validate_window():
    """Test the validate_window function."""
    input_data = pd.Series(range(1, 100))
    validate_window(
        input_data=input_data,
        window=20,
    )
