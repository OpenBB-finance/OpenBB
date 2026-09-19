"""Test Script parser."""

from datetime import datetime, timedelta

import pytest

from openbb_cli.controllers.script_parser import (
    match_and_return_openbb_keyword_date,
    parse_openbb_script,
)


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


def test_match_and_return_openbb_keyword_date():
    """Test the match_and_return_openbb_keyword_date function."""
    keyword = "$LASTFRIDAY"
    result = match_and_return_openbb_keyword_date(keyword)
    expected = ""
    if keyword == "$LASTFRIDAY":
        today = datetime.now()
        expected = today - timedelta(days=(today.weekday() + 3) % 7)
        if expected >= today:
            expected -= timedelta(days=7)
        expected = expected.strftime("%Y-%m-%d")
    assert result == expected


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
    if last_friday >= today:
        last_friday -= timedelta(days=7)
    expected_date = last_friday.strftime("%Y-%m-%d")
    assert match_and_return_openbb_keyword_date("$LASTFRIDAY") == expected_date


def test_date_keyword_last_january_returns_last_year_jan():
    """``$LASTJANUARY`` resolves to the most recent January 1st (this year or last)."""
    result = match_and_return_openbb_keyword_date("$LASTJANUARY")
    assert result.endswith("-01-01")


def test_date_keyword_last_december_returns_a_december_date():
    """``$LASTDECEMBER`` resolves to a Dec 1 date (this year or last depending on now)."""
    result = match_and_return_openbb_keyword_date("$LASTDECEMBER")
    assert result.endswith("-12-01")


def test_date_keyword_next_january_returns_a_january_date():
    """``$NEXTJANUARY`` returns a January 1 date (this year or next)."""
    result = match_and_return_openbb_keyword_date("$NEXTJANUARY")
    assert result.endswith("-01-01")


def test_date_keyword_next_friday_returns_a_future_date():
    """``$NEXTFRIDAY`` returns the next Friday's date (or today if Friday and equal)."""
    result = match_and_return_openbb_keyword_date("$NEXTFRIDAY")
    parsed = datetime.strptime(result, "%Y-%m-%d")
    assert parsed.weekday() == 4


def test_date_keyword_relative_days_ago():
    """``$1DAYSAGO`` resolves to (now - 1 day) — handled by the past regex (index 0)."""
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    result = match_and_return_openbb_keyword_date("$1DAYSAGO")
    assert result == yesterday


def test_date_keyword_relative_days_from_now():
    """``$2DAYSFROMNOW`` resolves to (now + 2 days) — past regex doesn't match, future does."""
    today = datetime.now()
    expected = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    result = match_and_return_openbb_keyword_date("$2DAYSFROMNOW")
    assert result == expected


def test_date_keyword_no_unit_match_returns_empty():
    """A bare ``$1DAYS`` (no AGO/FROMNOW suffix) does not match either regex → empty string."""
    assert match_and_return_openbb_keyword_date("$1DAYS") == ""


def test_date_keyword_last_sunday_falls_back_seven_days():
    """``$LASTSUNDAY`` exercises the ``today.weekday() <= target`` branch.

    Sunday is weekday 6 — no day of the week strictly exceeds it, so the
    weekday comparison always picks the second branch (subtracting 7 days
    before stepping to the requested weekday). That branch is the one
    coverage flagged previously.
    """
    today = datetime.now()
    result = match_and_return_openbb_keyword_date("$LASTSUNDAY")
    parsed = datetime.strptime(result, "%Y-%m-%d")
    # The result is a Sunday, and it is strictly in the past (not today
    # even when today is Sunday — the branch always subtracts a week).
    assert parsed.weekday() == 6
    assert parsed.date() < today.date()


def test_parse_openbb_script_multi_dollar_variable_warning(capsys):
    """Multi-dollar declarations emit a console warning but still set the variable."""
    from unittest.mock import patch

    with patch("openbb_cli.controllers.script_parser.session") as sess:
        error, script = parse_openbb_script(["$$VAR = hello", "echo $VAR"])
    assert error == ""
    assert script == "/echo hello"
    sess.console.print.assert_called()


def test_parse_openbb_script_index_zero_access():
    """``$VAR[0]`` accesses the first element of a list-valued variable."""
    error, script = parse_openbb_script(
        ["$DATES = 2022-01-01,2022-02-01", "echo $DATES[0]"]
    )
    assert error == ""
    assert script == "/echo 2022-01-01"


def test_parse_openbb_script_index_out_of_bounds():
    """Accessing ``$VAR[N]`` past the end produces a structured error."""
    error, _ = parse_openbb_script(["$X = a,b", "echo $X[5]"])
    assert "only has 2 elements" in error or "5 elements" in error or "index 5" in error


def test_parse_openbb_script_undeclared_variable_with_index():
    """Indexing an undeclared variable returns a 'not given' error."""
    error, _ = parse_openbb_script(["echo $MISSING[0]"])
    assert "not given" in error


def test_parse_openbb_script_undeclared_variable_with_index_nonzero():
    """``$MISSING[3]`` (non-zero index) on undeclared variable returns 'not given'."""
    error, _ = parse_openbb_script(["echo $MISSING[3]"])
    assert "not given" in error


def test_parse_openbb_script_slice_works_for_lists():
    """``$VAR[0:2]`` slices the list and joins by comma."""
    error, script = parse_openbb_script(["$VAR = a,b,c", "echo $VAR[0:2]"])
    assert error == ""
    assert "a,b" in script


def test_parse_openbb_script_slice_negative_index_returns_error():
    """Negative index without slicing → red error."""
    error, _ = parse_openbb_script(["$VAR = a,b", "echo $VAR[-5]"])
    assert "Negative index" in error or "not a value" in error


def test_parse_openbb_script_non_digit_index_returns_error():
    """Non-numeric index like ``$VAR[abc]`` → 'not a value' error."""
    error, _ = parse_openbb_script(["$VAR = a,b", "echo $VAR[abc]"])
    assert "not a value" in error


def test_parse_openbb_script_unknown_variable_resolves_via_keyword_date():
    """Undeclared variable that matches an OpenBB date keyword resolves to a date."""
    error, script = parse_openbb_script(["echo $LASTFRIDAY"])
    assert error == ""
    assert script != ""


def test_parse_openbb_script_unterminated_foreach_returns_error():
    """``foreach`` without ``end`` returns the dedicated red error."""
    error, _ = parse_openbb_script(
        [
            "foreach $$VAR in 2024-01-01,2024-02-01",
            "echo $$VAR",
        ]
    )
    assert "foreach loop that doesn't terminate" in error


def test_parse_openbb_script_value_replaces_string_value():
    """Single-string variable expansion (not a list)."""
    error, script = parse_openbb_script(["$NAME = world", "echo $NAME"])
    assert error == ""
    assert "world" in script


def test_parse_openbb_script_skips_comments():
    """Lines containing ``#`` are stripped before parsing."""
    error, script = parse_openbb_script(["# a comment", "echo hello"])
    assert error == ""
    assert "hello" in script


def test_parse_openbb_script_skips_reset_lines():
    """``reset`` / ``r`` lines are filtered out as preprocessing."""
    error, script = parse_openbb_script(["reset", "echo done"])
    assert error == ""
    assert "done" in script
    assert "/reset" not in script.split("/")[1] if "/" in script else True


def test_parse_openbb_script_foreach_with_unused_loop_variable_warns():
    """``foreach $$VAR in ...`` with body that doesn't reference $$VAR prints a warning."""
    from unittest.mock import patch

    with patch("openbb_cli.controllers.script_parser.session") as sess:
        error, script = parse_openbb_script(
            [
                "foreach $$DATE in 2024-01-01,2024-02-01",
                "echo nothing",
                "end",
            ]
        )
    assert error == ""
    sess.console.print.assert_called()


def test_parse_openbb_script_foreach_with_mismatched_var_returns_error():
    """``foreach $$X in ...`` followed by body using ``$$Y`` returns a red error."""
    error, script = parse_openbb_script(
        [
            "foreach $$DATE in 2024-01-01",
            "echo $$WRONG",
            "end",
        ]
    )
    assert "another var name" in error or script == ""


def test_parse_openbb_script_leading_slash_in_first_command():
    """A first command starting with ``/`` survives the home-prepending rule."""
    error, script = parse_openbb_script(["/equity"])
    assert error == ""
    assert script.startswith("/equity") or "equity" in script


def test_parse_openbb_script_strips_trailing_home():
    """A trailing ``/home/`` placeholder gets trimmed at the end of the assembly."""
    error, script = parse_openbb_script(["/equity", "/"])
    assert error == ""
    assert not script.endswith("/home/")


def test_parse_openbb_script_with_routines_args_replaces_argv():
    """``$ARGV[0]`` is replaced by the first script_inputs entry at parse time."""
    error, script = parse_openbb_script(["echo $ARGV[0]"], script_inputs=["AAPL"])
    assert error == ""
    assert "AAPL" in script


def test_date_keyword_last_monday_when_today_is_tuesday(freezer):
    """``$LASTMONDAY`` on a Tuesday returns the prior day."""
    freezer.move_to("2024-01-09")
    result = match_and_return_openbb_keyword_date("$LASTMONDAY")
    assert result == "2024-01-08"


def test_date_keyword_next_december_when_today_is_january(freezer):
    """``$NEXTDECEMBER`` from January resolves to **this year**'s December."""
    freezer.move_to("2024-01-15")
    result = match_and_return_openbb_keyword_date("$NEXTDECEMBER")
    assert result == "2024-12-01"


def test_date_keyword_next_monday_when_today_is_tuesday(freezer):
    """``$NEXTMONDAY`` on Tuesday resolves to next week's Monday."""
    freezer.move_to("2024-01-09")
    result = match_and_return_openbb_keyword_date("$NEXTMONDAY")
    assert result == "2024-01-15"


def test_date_keyword_next_friday_when_today_is_monday(freezer):
    """``$NEXTFRIDAY`` on Monday resolves to this week's Friday."""
    freezer.move_to("2024-01-08")
    result = match_and_return_openbb_keyword_date("$NEXTFRIDAY")
    assert result == "2024-01-12"


def test_parse_openbb_script_string_var_index_zero():
    """``$VAR[0]`` for a non-list string variable substitutes the whole string."""
    error, script = parse_openbb_script(["$DATE = 2022-01-01", "echo $DATE[0]"])
    assert error == ""
    assert "2022-01-01" in script


def test_parse_openbb_script_index_valid_nonzero():
    """``$VAR[N]`` for a valid in-bounds N replaces with that element."""
    error, script = parse_openbb_script(["$VAR = a,b,c", "echo $VAR[2]"])
    assert error == ""
    assert script == "/echo c"


def test_parse_openbb_script_slice_yields_empty_returns_error():
    """``$VAR[5:10]`` over a 2-elem list yields an empty slice → red error."""
    error, _ = parse_openbb_script(["$VAR = a,b", "echo $VAR[5:10]"])
    assert "foreach loop cannot run" in error


def test_parse_openbb_script_minus_nondigit_index_returns_error():
    """``$VAR[-abc]`` (minus + non-digit) hits the inner non-digit branch."""
    error, _ = parse_openbb_script(["$VAR = a,b", "echo $VAR[-abc]"])
    assert "not a value" in error


def test_parse_openbb_script_list_var_plain_reference_joins():
    """Plain ``$VAR`` reference where VAR is a list joins with comma."""
    error, script = parse_openbb_script(["$LIST = a,b,c", "echo $LIST"])
    assert error == ""
    assert script == "/echo a,b,c"
