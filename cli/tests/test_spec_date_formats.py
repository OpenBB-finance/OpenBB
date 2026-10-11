"""OpenAPI formats must control native CLI argument coercion."""

import pytest

from openbb_cli.dispatchers.spec import _normalize_parameter, parser_from_command_spec


@pytest.mark.parametrize(
    "fmt,name,description,expected",
    [
        ("date", "start_date", "format YYYY-MM-DD", "2026-01-02"),
        ("date", "from_datetime", "timestamp", "2026-01-02"),
        ("date-time", "when", None, "2026-01-02T00:00:00Z"),
    ],
)
def test_explicit_format_takes_precedence(fmt, name, description, expected):
    parameter = _normalize_parameter(
        {
            "name": name,
            "description": description,
            "schema": {"type": "string", "format": fmt},
        }
    )
    parser = parser_from_command_spec({"parameters": [parameter]})
    assert vars(parser.parse_args(["--" + name, "2026-01-02"]))[name] == expected
