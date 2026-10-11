"""Raw OpenAPI and cached spec parsers agree on boolean overrides."""

import pytest

from openbb_cli.dispatchers.openapi_schema import build_parser_from_operation
from openbb_cli.dispatchers.spec import parser_from_command_spec


@pytest.mark.parametrize("default", [True, False])
@pytest.mark.parametrize(
    "args, expected",
    [
        ([], None),
        (["--enabled"], True),
        (["--no-enabled"], False),
        (["--enabled", "--no-enabled"], False),
        (["--no-enabled", "--enabled"], True),
    ],
)
def test_boolean_defaults_can_be_overridden_with_parser_parity(default, args, expected):
    raw = build_parser_from_operation(
        {
            "parameters": [
                {"name": "enabled", "schema": {"type": "boolean", "default": default}}
            ]
        }
    )
    cached = parser_from_command_spec(
        {"parameters": [{"name": "enabled", "type": "boolean", "default": default}]}
    )
    expected = default if expected is None else expected
    assert raw.parse_args(args).enabled is expected
    assert cached.parse_args(args).enabled is expected
    assert "--no-enabled" in raw.format_help()


def test_undeclared_boolean_default_remains_false_and_unknown_flags_are_rejected():
    parser = build_parser_from_operation(
        {"parameters": [{"name": "enabled", "schema": {"type": "boolean"}}]}
    )
    assert parser.parse_args([]).enabled is False
    with pytest.raises(SystemExit):
        parser.parse_args(["--unknown"])


def test_existing_generated_negative_option_collision_matches_cached_parser():
    raw = build_parser_from_operation(
        {
            "parameters": [
                {"name": "enabled", "schema": {"type": "boolean", "default": True}},
                {"name": "no-enabled", "schema": {"type": "string"}},
            ]
        }
    )
    cached = parser_from_command_spec(
        {
            "parameters": [
                {"name": "enabled", "type": "boolean", "default": True},
                {"name": "no-enabled", "type": "string"},
            ]
        }
    )
    assert vars(raw.parse_args(["--no-enabled"])) == vars(
        cached.parse_args(["--no-enabled"])
    )
