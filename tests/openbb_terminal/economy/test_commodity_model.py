"""Test commodity model."""

import pytest

from openbb_terminal.economy import commodity_model


def test_format_number():
    fmt_number = commodity_model.format_number("1.2T")
    assert fmt_number == 1_200_000_000_000
    assert isinstance(fmt_number, float)


@pytest.mark.record_http
def test_get_debt():
    df = commodity_model.get_debt()
    assert df is not None
    assert not df.empty
