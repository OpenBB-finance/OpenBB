"""Test the provider validators."""

import pytest
from openbb_core.provider.utils.validators import check_single_value


@pytest.mark.parametrize(
    "field, value, expected",
    [
        ("test", "SYMBOL", "SYMBOL"),
        ("test", None, None),
        ("test", "", ""),
        ("test", "SYMBOL1,SYMBOL2", ValueError),
        ("test", "SYMBOL1;SYMBOL2", ValueError),
    ],
)
def test_check_single_value(field, value, expected):
    if expected is ValueError:
        with pytest.raises(ValueError):
            check_single_value(field, value)
    else:
        assert check_single_value(field, value) == expected
