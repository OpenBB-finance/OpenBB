"""Exact integer values must survive numeric schema coercion."""

import pytest

from openbb_cli.dispatchers.http import _coerce_response_value
from openbb_cli.dispatchers.socrata import _coerce_choices_to_type


@pytest.mark.parametrize("kind", ["number", "money", "percent", "double"])
@pytest.mark.parametrize(
    "text,expected",
    [
        ("9007199254740993", 9007199254740993),
        ("-9007199254740993", -9007199254740993),
        ("9.007199254740993e15", 9007199254740993),
        ("42.000", 42),
        ("1.25", 1.25),
        ("not-a-number", "not-a-number"),
        ("NaN", "NaN"),
        ("Infinity", "Infinity"),
        ("1e1000000000", "1e1000000000"),
        ("-1e1000000000", "-1e1000000000"),
    ],
)
def test_numeric_response_retains_precision(kind, text, expected):
    assert _coerce_response_value(text, kind, "") == expected


@pytest.mark.parametrize("kind", ["number", "money", "percent", "double"])
def test_numeric_choices_preserve_digits_and_ignore_nonfinite(kind):
    assert _coerce_choices_to_type(
        [
            "9007199254740993",
            "-9007199254740993",
            "1.25",
            None,
            "NaN",
            "Infinity",
            "1e1000000000",
            "oops",
        ],
        kind,
    ) == [9007199254740993, -9007199254740993, 1.25]


def test_nonnumeric_controls():
    assert (
        _coerce_response_value("9007199254740993", "string", "") == "9007199254740993"
    )
    assert _coerce_choices_to_type(["x"], "text") == ["x"]
