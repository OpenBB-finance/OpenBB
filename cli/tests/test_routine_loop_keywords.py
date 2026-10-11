"""Literal foreach text is data, while standalone loop headers still expand."""

import pytest

from openbb_cli.controllers.script_parser import parse_openbb_script


@pytest.mark.parametrize(
    "line", ["echo foreach", "echo before-foreach-after", "echo foreach $$VAR in A,B"]
)
def test_foreach_in_arguments_is_not_a_loop(line):
    assert parse_openbb_script([line]) == ("", "/" + line)


def test_real_foreach_control():
    assert parse_openbb_script(["foreach $$VAR in A,B", "echo $$VAR", "end"]) == (
        "",
        "/echo A/echo B",
    )
