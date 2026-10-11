"""Comments must not discard commands with literal hash arguments."""

import pytest

from openbb_cli.controllers.script_parser import parse_openbb_script


@pytest.mark.parametrize(
    "line,expected",
    [
        ("echo '#daily'", "echo '#daily'"),
        ('echo "#daily"', 'echo "#daily"'),
        ("echo fragment#section", "echo fragment#section"),
        (r"echo \#daily", r"echo \#daily"),
        ("echo kept # comment", "echo kept"),
        ("# comment", ""),
    ],
)
def test_routine_comment_boundaries(line, expected):
    assert parse_openbb_script([line]) == ("", "/" + expected if expected else "")
