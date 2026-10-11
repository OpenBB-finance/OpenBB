"""Routine reset recognition should not consume command arguments."""

import pytest

from openbb_cli.controllers.script_parser import is_reset, parse_openbb_script


@pytest.mark.parametrize(
    "line", ["echo reset", "echo preset", "echo resettable", "echo --name reset"]
)
def test_reset_in_arguments_preserves_command(line):
    assert not is_reset(line)
    assert parse_openbb_script([line]) == ("", "/" + line)


@pytest.mark.parametrize("line", ["reset", "r", " reset ", "r\n"])
def test_standalone_reset_is_filtered(line):
    assert is_reset(line)
    assert parse_openbb_script([line, "echo kept"]) == ("", "/echo kept")
