from datetime import date

import pytest

from openbb_famafrench.utils.missing_values import (
    is_missing_value,
    replace_missing_values,
)


@pytest.mark.parametrize(
    "value",
    [None, float("nan"), -99.99, -999, -999.0, "-99.99", " -99.990", "-999", "-999.00"],
)
def test_is_missing_value_true(value):
    assert is_missing_value(value) is True


@pytest.mark.parametrize(
    "value",
    [
        0.0,
        -99.98,
        -9.99,
        12,
        "1.5",
        "-9.5",
        "-9x",
        "Lo 30",
        "2020-01-31",
        True,
        date(2020, 1, 31),
    ],
)
def test_is_missing_value_false(value):
    assert is_missing_value(value) is False


def test_replace_missing_values():
    records = [
        {"Date": "2020-01-31", "Mkt": "-99.99", "High": 1.5, "Firms": "12"},
        {"Date": "2020-02-29", "Mkt": 2.0, "High": -999.0, "Firms": "-999"},
    ]
    assert replace_missing_values(records, integer_fields=("Firms",)) == [
        {"Date": "2020-01-31", "Mkt": None, "High": 1.5, "Firms": 12},
        {"Date": "2020-02-29", "Mkt": 2.0, "High": None, "Firms": None},
    ]
