"""Variable prefixes must not rewrite other complete references."""

import pytest

from openbb_cli.controllers.script_parser import parse_openbb_script


@pytest.mark.parametrize(
    "line,expected",
    [
        ("echo $A $AB", "/echo one two"),
        ("echo $AB $A $AB", "/echo two one two"),
        ("echo $A[0] $AB", "/echo one two"),
    ],
)
def test_variable_prefixes_expand_independently(line, expected):
    assert parse_openbb_script(["$A = one", "$AB = two", line]) == ("", expected)
