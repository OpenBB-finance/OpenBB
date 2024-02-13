"""Test the provider validators."""

import pytest
from openbb_core.provider.utils.validators import check_single_value


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SYMBOL", "SYMBOL"),
        (None, None),
        ("", ""),
        ("SYMBOL1,SYMBOL2", ValueError),
        ("SYMBOL1;SYMBOL2", ValueError),
    ],
)
def test_check_single_value(value, expected):
    if expected is ValueError:
        with pytest.raises(ValueError):
            check_single_value(value)
    else:
        assert check_single_value(value) == expected
