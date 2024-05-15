"""Test Script parser."""

from datetime import datetime, timedelta

import pytest
from openbb_cli.controllers.script_parser import (
    match_and_return_openbb_keyword_date,
    parse_openbb_script,
)

# pylint: disable=import-outside-toplevel, unused-variable, line-too-long


@pytest.mark.parametrize(
    "command, expected",
    [
        ("reset", True),
        ("r", True),
        ("r\n", True),
        ("restart", False),
    ],
)
def test_is_reset(command, expected):
    """Test the is_reset function."""
    from openbb_cli.controllers.script_parser import is_reset

    assert is_reset(command) == expected


@pytest.mark.parametrize(
    "keyword, expected_date",
    [
        (
            "$LASTFRIDAY",
            (
                datetime.now()
                - timedelta(days=((datetime.now().weekday() - 4) % 7 + 7) % 7)
            ).strftime("%Y-%m-%d"),
        ),
    ],
)
def test_match_and_return_openbb_keyword_date(keyword, expected_date):
    """Test the match_and_return_openbb_keyword_date function."""
    result = match_and_return_openbb_keyword_date(keyword)
    assert result == expected_date


def test_parse_openbb_script_basic():
    """Test the parse_openbb_script function."""
    raw_lines = ["echo 'Hello World'"]
    error, script = parse_openbb_script(raw_lines)
    assert error == ""
    assert script == "/echo 'Hello World'"


def test_parse_openbb_script_with_variable():
    """Test the parse_openbb_script function."""
    raw_lines = ["$VAR = 2022-01-01", "echo $VAR"]
    error, script = parse_openbb_script(raw_lines)
    assert error == ""
    assert script == "/echo 2022-01-01"


def test_parse_openbb_script_with_foreach_loop():
    """Test the parse_openbb_script function."""
    raw_lines = ["foreach $$DATE in 2022-01-01,2022-01-02", "echo $$DATE", "end"]
    error, script = parse_openbb_script(raw_lines)
    assert error == ""
    assert script == "/echo 2022-01-01/echo 2022-01-02"


def test_parse_openbb_script_with_error():
    """Test the parse_openbb_script function."""
    raw_lines = ["$VAR = ", "echo $VAR"]
    error, script = parse_openbb_script(raw_lines)
    assert "Variable $VAR not given" in error


@pytest.mark.parametrize(
    "line, expected",
    [
        (
            "foreach $$VAR in 2022-01-01",
            "[red]The script has a foreach loop that doesn't terminate. Add the keyword 'end' to explicitly terminate loop[/red]",  # noqa: E501
        ),
        ("echo Hello World", ""),
        (
            "end",
            "[red]The script has a foreach loop that terminates before it gets started. Add the keyword 'foreach' to explicitly start loop[/red]",  # noqa: E501
        ),
    ],
)
def test_parse_openbb_script_foreach_errors(line, expected):
    """Test the parse_openbb_script function."""
    error, script = parse_openbb_script([line])
    assert error == expected


def test_date_keyword_last_friday():
    """Test the match_and_return_openbb_keyword_date function."""
    today = datetime.now()
    last_friday = today - timedelta(days=(today.weekday() - 4 + 7) % 7)
    if last_friday > today:
        last_friday -= timedelta(days=7)
    expected_date = last_friday.strftime("%Y-%m-%d")
    assert match_and_return_openbb_keyword_date("$LASTFRIDAY") == expected_date
