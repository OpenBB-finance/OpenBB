"""Native parsers must honor exclusive schema alternatives."""

import argparse

import pytest

from openbb_cli.dispatchers.openapi_schema import (
    _resolve_schema,
    parameter_to_kwargs,
    request_body_parameters,
)


@pytest.mark.parametrize(
    "schema,expected",
    [
        ({"oneOf": [{"type": "integer"}, {"type": "null"}]}, (int, [], False)),
        (
            {
                "oneOf": [
                    {"type": "integer", "enum": [1, 2]},
                    {"type": "integer", "enum": [3]},
                ]
            },
            (int, [1, 2, 3], False),
        ),
        ({"oneOf": [{"const": "up"}, {"const": "down"}]}, (str, ["up", "down"], False)),
        ({"oneOf": [{"type": "string"}, {"type": "integer"}]}, (str, [], False)),
    ],
)
def test_oneof_schema_types(schema, expected):
    assert _resolve_schema(schema) == expected


def test_oneof_integer_enum_uses_native_argparse_conversion():
    parser = argparse.ArgumentParser()
    result = parameter_to_kwargs(
        {
            "name": "count",
            "schema": {
                "oneOf": [
                    {"type": "integer", "enum": [1]},
                    {"type": "integer", "enum": [2]},
                ]
            },
        }
    )
    assert result is not None
    flag, kwargs = result
    parser.add_argument(flag, **kwargs)
    assert parser.parse_args(["--count", "2"]).count == 2
    with pytest.raises(SystemExit):
        parser.parse_args(["--count", "3"])


def test_unrestricted_oneof_branch_does_not_inherit_enum_restriction():
    schema = {"oneOf": [{"type": "string"}, {"type": "string", "enum": ["restricted"]}]}
    parser = argparse.ArgumentParser()
    result = parameter_to_kwargs({"name": "mode", "schema": schema})
    assert result is not None
    flag, kwargs = result
    parser.add_argument(flag, **kwargs)
    assert parser.parse_args(["--mode", "other"]).mode == "other"


def test_object_alternative_body_field_decodes_json():
    body = {
        "type": "object",
        "properties": {
            "config": {
                "oneOf": [
                    {"type": "object", "properties": {"mode": {"type": "string"}}},
                    {"type": "null"},
                ]
            }
        },
    }
    parameter = request_body_parameters(body)[0]
    parser = argparse.ArgumentParser()
    result = parameter_to_kwargs(parameter)
    assert result is not None
    flag, kwargs = result
    parser.add_argument(flag, **kwargs)
    assert parser.parse_args(["--config", '{"mode":"safe"}']).config == {"mode": "safe"}
    assert parser.parse_args(["--config", "null"]).config is None
