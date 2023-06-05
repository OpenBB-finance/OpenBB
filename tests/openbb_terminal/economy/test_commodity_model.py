"""Test commodity model."""

import pytest

from openbb_terminal.economy import commodity_model


def test_format_number():
    fmt_number = commodity_model.format_number("1.2T")
    assert fmt_number == 1_200_000_000_000
    assert isinstance(fmt_number, float)


@pytest.mark.vcr
def test_get_debt(recorder):
    df = commodity_model.get_debt()
    recorder.capture(df)
