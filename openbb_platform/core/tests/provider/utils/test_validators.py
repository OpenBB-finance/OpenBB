"""Test the provider validators."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.validators import check_single_value


@pytest.mark.parametrize(
    "value, expected",
    [
        ("SYMBOL", "SYMBOL"),
        (None, None),
        ("", ""),
        ("SYMBOL1,SYMBOL2", OpenBBError),
        ("SYMBOL1;SYMBOL2", OpenBBError),
    ],
)
def test_check_single_value(value, expected):
    if expected is OpenBBError:
        with pytest.raises(OpenBBError):
            check_single_value(value)
    else:
        assert check_single_value(value) == expected
