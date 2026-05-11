"""Tests for the OpenAPI schema loader.

These exercise the pure-translation layer against synthetic spec fragments —
no live server required. The goal is to lock in the parameter → argparse
mapping behavior so it stays consistent as the CLI grows to consume the spec
from a remote ``openbb-platform-api`` server.
"""

from __future__ import annotations

import argparse

import pytest

from openbb_cli.dispatchers.openapi_schema import (
    _provider_choices,
    _resolve_schema,
    build_command_index,
    build_parser_from_operation,
    build_reference,
    build_router_map,
    parameter_to_kwargs,
    url_to_command,
)


def test_resolve_schema_primitive_string():
    assert _resolve_schema({"type": "string"}) == (str, [], False)


def test_resolve_schema_primitive_int():
    assert _resolve_schema({"type": "integer"}) == (int, [], False)


def test_resolve_schema_primitive_number():
    assert _resolve_schema({"type": "number"}) == (float, [], False)


def test_resolve_schema_boolean():
    assert _resolve_schema({"type": "boolean"}) == (bool, [], False)


def test_resolve_schema_enum():
    py_type, choices, is_list = _resolve_schema({"type": "string", "enum": ["a", "b"]})
    assert py_type is str and choices == ["a", "b"] and is_list is False


def test_resolve_schema_array_of_strings():
    py_type, choices, is_list = _resolve_schema(
        {"type": "array", "items": {"type": "string"}}
    )
    assert py_type is str and is_list is True and choices == []


def test_resolve_schema_optional_collapses_to_inner():
    """``anyOf: [{type: string}, {type: null}]`` → str."""
    py_type, _, _ = _resolve_schema({"anyOf": [{"type": "string"}, {"type": "null"}]})
    assert py_type is str


def test_resolve_schema_union_of_str_int_falls_back_to_str():
    py_type, _, _ = _resolve_schema(
        {"anyOf": [{"type": "string"}, {"type": "integer"}]}
    )
    assert py_type is str


def test_resolve_schema_union_of_enums_unions_choices():
    _, choices, _ = _resolve_schema(
        {
            "anyOf": [
                {"type": "string", "enum": ["a", "b"]},
                {"type": "string", "enum": ["b", "c"]},
            ]
        }
    )
    assert set(choices) == {"a", "b", "c"}


def test_resolve_schema_array_in_union_marked_as_list():
    _, _, is_list = _resolve_schema(
        {"anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]}
    )
    assert is_list is True


def test_resolve_schema_const_treated_as_single_choice():
    py_type, choices, _ = _resolve_schema({"const": "fred"})
    assert py_type is str and choices == ["fred"]


def test_provider_choices_skips_reserved_keys():
    schema = {
        "type": "string",
        "enum": ["a", "b"],
        "default": "a",
        "title": "x",
    }
    assert _provider_choices(schema) == []


def test_provider_choices_unions_per_provider_choices():
    schema = {
        "type": "string",
        "fmp": {"choices": ["1m", "5m"]},
        "yfinance": {"choices": ["5m", "1d"]},
    }
    assert set(_provider_choices(schema)) == {"1m", "5m", "1d"}


def test_parameter_to_kwargs_skips_chart():
    """``chart`` is handled by the output adapter, not the command parser."""
    assert parameter_to_kwargs({"name": "chart", "schema": {"type": "boolean"}}) is None


def test_parameter_to_kwargs_required_string():
    flag, kwargs = parameter_to_kwargs(
        {"name": "symbol", "required": True, "schema": {"type": "string"}}
    )
    assert flag == "--symbol"
    assert kwargs["type"] is str
    assert kwargs.get("required") is True


def test_parameter_to_kwargs_optional_with_default():
    flag, kwargs = parameter_to_kwargs(
        {
            "name": "limit",
            "required": False,
            "schema": {"type": "integer", "default": 10},
        }
    )
    assert flag == "--limit"
    assert kwargs["type"] is int
    assert kwargs["default"] == 10
    assert "required" not in kwargs


def test_parameter_to_kwargs_boolean_flag():
    _, kwargs = parameter_to_kwargs(
        {"name": "verbose", "schema": {"type": "boolean", "default": False}}
    )
    assert kwargs["action"] == "store_true"
    assert kwargs["default"] is False


def test_parameter_to_kwargs_list_uses_nargs_plus():
    _, kwargs = parameter_to_kwargs(
        {
            "name": "symbols",
            "schema": {"type": "array", "items": {"type": "string"}},
        }
    )
    assert kwargs["nargs"] == "+"


def test_parameter_to_kwargs_enum_emits_choices():
    _, kwargs = parameter_to_kwargs(
        {"name": "side", "schema": {"type": "string", "enum": ["buy", "sell"]}}
    )
    assert kwargs["choices"] == ["buy", "sell"]


def test_parameter_to_kwargs_provider_choices_unioned_with_enum():
    """Per-provider ``choices`` are merged with the schema-level enum."""
    _, kwargs = parameter_to_kwargs(
        {
            "name": "interval",
            "schema": {
                "type": "string",
                "enum": ["1m", "5m"],
                "fmp": {"choices": ["5m", "1h"]},
                "yfinance": {"choices": ["1d"]},
            },
        }
    )
    assert set(kwargs["choices"]) == {"1m", "5m", "1h", "1d"}


def test_parameter_to_kwargs_help_percent_escaped():
    """A ``%`` in the description is doubled so argparse's validator accepts it."""
    _, kwargs = parameter_to_kwargs(
        {"name": "x", "description": "100% sure", "schema": {"type": "string"}}
    )
    assert kwargs["help"] == "100%% sure"


def test_parameter_to_kwargs_no_name_returns_none():
    assert parameter_to_kwargs({"schema": {"type": "string"}}) is None


def test_build_parser_uses_operation_metadata():
    op = {
        "operationId": "my_cmd",
        "description": "Do the thing.",
        "parameters": [
            {"name": "name", "required": True, "schema": {"type": "string"}},
            {"name": "n", "schema": {"type": "integer", "default": 5}},
        ],
    }
    parser = build_parser_from_operation(op)
    assert parser.prog == "my_cmd"
    assert "Do the thing." in (parser.description or "")
    ns = parser.parse_args(["--name", "x", "--n", "7"])
    assert ns.name == "x" and ns.n == 7


def test_build_parser_required_arg_enforced():
    op = {
        "operationId": "x",
        "parameters": [
            {"name": "needed", "required": True, "schema": {"type": "string"}}
        ],
    }
    parser = build_parser_from_operation(op)
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_build_parser_invalid_choice_rejected():
    op = {
        "operationId": "x",
        "parameters": [
            {
                "name": "side",
                "schema": {"type": "string", "enum": ["buy", "sell"]},
            }
        ],
    }
    parser = build_parser_from_operation(op)
    with pytest.raises(SystemExit):
        parser.parse_args(["--side", "hold"])


def test_build_parser_skips_chart_parameter():
    op = {
        "operationId": "x",
        "parameters": [
            {"name": "chart", "schema": {"type": "boolean"}},
            {"name": "symbol", "schema": {"type": "string", "default": "X"}},
        ],
    }
    parser = build_parser_from_operation(op)
    optstrings = {opt for action in parser._actions for opt in action.option_strings}
    assert "--chart" not in optstrings
    assert "--symbol" in optstrings


def test_build_parser_skips_invalid_parameter_silently():
    """Duplicate flags raise ``ArgumentError`` and are skipped — first wins."""
    op = {
        "operationId": "x",
        "parameters": [
            {"name": "dup", "schema": {"type": "string", "default": "first"}},
            {"name": "dup", "schema": {"type": "integer", "default": 99}},
        ],
    }
    parser = build_parser_from_operation(op)
    ns = parser.parse_args([])
    assert ns.dup == "first"


@pytest.mark.parametrize(
    "url, expected",
    [
        ("/api/v1/equity/price/historical", "equity.price.historical"),
        ("/api/v1/commodity/price/spot", "commodity.price.spot"),
        ("/api/v1/economy", "economy"),
        ("/economy/cpi", "economy.cpi"),
    ],
)
def test_url_to_command(url, expected):
    assert url_to_command(url) == expected


def test_url_to_command_custom_prefix():
    assert url_to_command("/api/v2/foo/bar", api_prefix="/api/v2") == "foo.bar"


def test_build_command_index_keyed_by_dotted_path():
    spec = {
        "paths": {
            "/api/v1/equity/price/historical": {
                "get": {
                    "operationId": "eqh",
                    "parameters": [
                        {
                            "name": "symbol",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                }
            }
        }
    }
    index = build_command_index(spec)
    assert "equity.price.historical" in index
    assert isinstance(index["equity.price.historical"], argparse.ArgumentParser)


def test_build_command_index_skips_paths_without_known_method():
    spec = {"paths": {"/api/v1/x": {"delete": {"operationId": "x"}}}}
    assert build_command_index(spec) == {}


def test_build_command_index_uses_post_when_get_missing():
    spec = {
        "paths": {
            "/api/v1/run": {
                "post": {
                    "operationId": "run",
                    "parameters": [{"name": "in", "schema": {"type": "string"}}],
                }
            }
        }
    }
    assert "run" in build_command_index(spec)


def test_build_router_map_classifies_menus_and_commands():
    spec = {
        "paths": {
            "/api/v1/commodity/price/spot": {"get": {"operationId": "x"}},
            "/api/v1/equity/quote": {"get": {"operationId": "y"}},
        }
    }
    out = build_router_map(spec)
    assert out["commodity"] == "menu"
    assert out["commodity.price"] == "menu"
    assert out["commodity.price.spot"] == "command"
    assert out["equity"] == "menu"
    assert out["equity.quote"] == "command"


def test_build_router_map_ignores_paths_without_methods():
    spec = {"paths": {"/api/v1/foo": {}}}
    assert build_router_map(spec) == {}


def test_build_reference_paths_carry_descriptions():
    spec = {
        "paths": {
            "/api/v1/equity/quote": {
                "get": {
                    "operationId": "x",
                    "summary": "Quote",
                    "description": "Get a quote.",
                    "tags": ["equity"],
                }
            }
        },
        "tags": [{"name": "equity", "description": "Equity data."}],
    }
    ref = build_reference(spec)
    assert ref["paths"]["/equity/quote"]["description"] == "Get a quote."
    assert ref["routers"]["/equity/"]["description"] == "Equity data."


def test_build_reference_falls_back_to_summary_when_no_description():
    spec = {
        "paths": {
            "/api/v1/equity/quote": {
                "get": {"operationId": "x", "summary": "Just a quote.", "tags": []}
            }
        }
    }
    assert (
        build_reference(spec)["paths"]["/equity/quote"]["description"]
        == "Just a quote."
    )


def test_build_reference_router_default_description_when_tag_missing():
    spec = {
        "paths": {
            "/api/v1/x/y": {"get": {"operationId": "z", "tags": ["unknown_tag"]}},
        },
        "tags": [],
    }
    ref = build_reference(spec)
    assert ref["routers"]["/x/"]["description"] == ""


def test_resolve_schema_anyof_all_null_returns_str():
    """Edge: ``anyOf: [{type:null}]`` (no non-null types) collapses to str."""
    py_type, choices, is_list = _resolve_schema({"anyOf": [{"type": "null"}]})
    assert py_type is str and choices == [] and is_list is False


def test_resolve_schema_array_in_array_recurses():
    py_type, choices, is_list = _resolve_schema(
        {"type": "array", "items": {"type": "integer", "enum": [1, 2]}}
    )
    assert py_type is int and is_list is True and choices == [1, 2]


def test_resolve_schema_union_skips_duplicate_enum_values():
    """Duplicate enum values across union members are de-duped."""
    _, choices, _ = _resolve_schema(
        {
            "anyOf": [
                {"type": "string", "enum": ["a", "b"]},
                {"type": "string", "enum": ["a", "c"]},
            ]
        }
    )
    assert choices == ["a", "b", "c"]


def test_strip_placeholders_unbalanced_brace_breaks():
    """``{foo without closing brace`` is left untouched (the while loop breaks)."""
    from openbb_cli.dispatchers.openapi_schema import _strip_placeholders

    assert _strip_placeholders("{foo") == "{foo"


def test_strip_placeholders_close_before_open_breaks_loop():
    """``}foo{`` enters the loop (both braces present) but ``find('}', i)`` returns -1."""
    from openbb_cli.dispatchers.openapi_schema import _strip_placeholders

    assert _strip_placeholders("}foo{") == "}foo{"


def test_url_to_command_with_no_prefix_match_uses_full_path():
    """Custom prefix that isn't actually present in the URL → no stripping."""
    from openbb_cli.dispatchers.openapi_schema import url_to_command

    assert url_to_command("/x/y/z", api_prefix="/api/v1") == "x.y.z"


def test_detect_api_prefix_empty_spec_falls_back_to_default():
    from openbb_cli.dispatchers.openapi_schema import detect_api_prefix

    assert detect_api_prefix({}) == "/api/v1"
    assert detect_api_prefix({"paths": {}}) == "/api/v1"


def test_detect_api_prefix_two_paths_diverging_immediately():
    from openbb_cli.dispatchers.openapi_schema import detect_api_prefix

    spec = {"paths": {"/foo/x": {}, "/bar/y": {}}}
    assert detect_api_prefix(spec) == ""


def test_detect_api_prefix_finds_common_segments():
    from openbb_cli.dispatchers.openapi_schema import detect_api_prefix

    spec = {"paths": {"/api/foo/x": {}, "/api/bar/y": {}}}
    assert detect_api_prefix(spec) == "/api"


def test_parse_spec_text_recognizes_json_object():
    from openbb_cli.dispatchers.openapi_schema import _parse_spec_text

    out = _parse_spec_text('{"openapi": "3.0.0"}')
    assert out == {"openapi": "3.0.0"}


def test_parse_spec_text_recognizes_yaml_via_content_type():
    from openbb_cli.dispatchers.openapi_schema import _parse_spec_text

    out = _parse_spec_text("openapi: 3.0.0\npaths: {}", content_type="application/yaml")
    assert out == {"openapi": "3.0.0", "paths": {}}


def test_parse_spec_text_recognizes_yaml_via_heuristic():
    from openbb_cli.dispatchers.openapi_schema import _parse_spec_text

    out = _parse_spec_text("openapi: 3.0.0")
    assert out == {"openapi": "3.0.0"}


def test_parse_spec_text_swagger_heuristic():
    from openbb_cli.dispatchers.openapi_schema import _parse_spec_text

    out = _parse_spec_text("swagger: '2.0'\ninfo:\n  title: x")
    assert out["swagger"] == "2.0"


def test_parse_spec_text_falls_back_to_yaml_when_json_fails():
    """Last-resort branch: not JSON-shape, no content-type hint, no heuristic match."""
    from openbb_cli.dispatchers.openapi_schema import _parse_spec_text

    out = _parse_spec_text("foo: bar")
    assert out == {"foo": "bar"}


def test_parse_spec_text_recognizes_json_array_form():
    """A bare JSON array also goes through the JSON branch."""
    from openbb_cli.dispatchers.openapi_schema import _parse_spec_text

    assert _parse_spec_text("[1, 2]") == [1, 2]


def test_fetch_openapi_default_path_and_user_agent(monkeypatch):
    """Default appends ``/openapi.json`` and merges the default User-Agent."""
    from openbb_cli.dispatchers import openapi_schema

    captured: dict[str, object] = {}

    class _Resp:
        status_code = 200
        text = '{"openapi": "3.0.0"}'
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            return None

    def fake_get(url, *, timeout, follow_redirects, headers, params=None):
        captured["url"] = url
        captured["headers"] = headers
        return _Resp()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    out = openapi_schema.fetch_openapi("http://h")
    assert out == {"openapi": "3.0.0"}
    assert captured["url"] == "http://h/openapi.json"
    assert captured["headers"]["User-Agent"] == "openbb-cli/1.0"


def test_fetch_openapi_custom_path_appended(monkeypatch):
    from openbb_cli.dispatchers import openapi_schema

    captured: dict[str, object] = {}

    class _Resp:
        status_code = 200
        text = "{}"
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            return None

    def fake_get(url, *, timeout, follow_redirects, headers, params=None):
        captured["url"] = url
        return _Resp()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    openapi_schema.fetch_openapi("http://h/", path="/static/spec.yml")
    assert captured["url"] == "http://h/static/spec.yml"


def test_fetch_openapi_full_url_path_passes_through(monkeypatch):
    """If ``path`` is already absolute, ``base_url`` is ignored."""
    from openbb_cli.dispatchers import openapi_schema

    captured: dict[str, object] = {}

    class _Resp:
        status_code = 200
        text = "{}"
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            return None

    def fake_get(url, *, timeout, follow_redirects, headers, params=None):
        captured["url"] = url
        return _Resp()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    openapi_schema.fetch_openapi("http://h", path="https://elsewhere/spec.json")
    assert captured["url"] == "https://elsewhere/spec.json"


def test_resolve_schema_union_with_array_member_marks_is_list():
    """``anyOf: [array, scalar]`` propagates ``is_list=True``."""
    _, _, is_list = _resolve_schema(
        {
            "anyOf": [
                {"type": "array", "items": {"type": "string"}},
                {"type": "string"},
            ]
        }
    )
    assert is_list is True


def test_strip_placeholders_collapses_balanced_braces():
    """``latest.{format}`` → ``latest``."""
    from openbb_cli.dispatchers.openapi_schema import _strip_placeholders

    assert _strip_placeholders("latest.{format}") == "latest"


def test_detect_api_prefix_breaks_when_common_emptied():
    """Three paths whose very first segment differs across them hit the
    ``not common: break`` arm."""
    from openbb_cli.dispatchers.openapi_schema import detect_api_prefix

    spec = {"paths": {"/x/y": {}, "a/y/z": {}, "/x/q": {}}}
    detect_api_prefix(spec)


def test_build_router_map_skips_empty_command():
    """A URL that strips to an empty dotted command is skipped."""
    from openbb_cli.dispatchers.openapi_schema import build_router_map

    spec = {"paths": {"/api/v1": {"get": {"operationId": "x"}}}}
    assert build_router_map(spec) == {}


def test_build_reference_skips_paths_without_known_methods():
    """A path with only DELETE/PUT is not surfaced."""
    from openbb_cli.dispatchers.openapi_schema import build_reference

    spec = {"paths": {"/api/v1/x": {"delete": {"operationId": "x"}}}}
    out = build_reference(spec)
    assert out["paths"] == {}
    assert out["routers"] == {}


def test_build_reference_dedupes_menu_paths():
    """Two paths under the same menu → router entry recorded once."""
    from openbb_cli.dispatchers.openapi_schema import build_reference

    spec = {
        "paths": {
            "/api/v1/equity/quote": {"get": {"operationId": "q", "tags": ["e"]}},
            "/api/v1/equity/profile": {"get": {"operationId": "p", "tags": ["e"]}},
        },
        "tags": [{"name": "e", "description": "Equity."}],
    }
    out = build_reference(spec)
    assert len(out["routers"]) == 1
    assert out["routers"]["/equity/"]["description"] == "Equity."


def test_fetch_openapi_merges_caller_headers(monkeypatch):
    """Caller-supplied headers are merged with the default User-Agent."""
    from openbb_cli.dispatchers import openapi_schema

    captured: dict[str, object] = {}

    class _Resp:
        status_code = 200
        text = "{}"
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            return None

    def fake_get(url, *, timeout, follow_redirects, headers, params=None):
        captured["headers"] = headers
        return _Resp()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    openapi_schema.fetch_openapi("http://h", headers={"Authorization": "Bearer x"})
    assert captured["headers"]["User-Agent"] == "openbb-cli/1.0"
    assert captured["headers"]["Authorization"] == "Bearer x"


# --- Provider section parsing ---


def test_parse_provider_sections_separates_tagged_from_untagged():
    from openbb_cli.dispatchers.openapi_schema import parse_provider_sections

    text = (
        "Shared sentence with no tag.;\n    "
        "FMP-only bit. (provider: fmp);\n    "
        "Both intrinio and cboe. (provider: intrinio,cboe)"
    )
    tagged, has_untagged = parse_provider_sections(text)
    assert tagged == {"fmp", "intrinio", "cboe"}
    assert has_untagged is True


def test_parse_provider_sections_all_tagged():
    from openbb_cli.dispatchers.openapi_schema import parse_provider_sections

    text = "X. (provider: cboe);\n    Y. (provider: fmp)"
    tagged, has_untagged = parse_provider_sections(text)
    assert tagged == {"cboe", "fmp"}
    assert has_untagged is False


def test_param_provider_membership_description_takes_priority():
    """When the description has an untagged section, the param applies to ALL."""
    from openbb_cli.dispatchers.openapi_schema import param_provider_membership

    # Schema has explicit per-provider keys EXCLUDING intrinio,
    # but the description has an untagged section → applies to all.
    schema = {
        "type": "string",
        "cboe": {"x": 1},
        "fmp": {"x": 1},
    }
    desc = "Shared description.;\n    Intrinio variant. (provider: intrinio)"
    membership = param_provider_membership(
        schema, desc, providers_set={"cboe", "fmp", "intrinio"}
    )
    # Untagged section signals "shared" → empty list
    assert membership == []


def test_param_provider_membership_returns_only_tagged_when_no_untagged():
    """All sections tagged → return the union (intersected with declared providers)."""
    from openbb_cli.dispatchers.openapi_schema import param_provider_membership

    desc = "X. (provider: cboe);\n    Y. (provider: fmp,unknown_provider)"
    membership = param_provider_membership(
        {}, desc, providers_set={"cboe", "fmp", "intrinio"}
    )
    # unknown_provider drops out (not in declared set), order independent
    assert sorted(membership) == ["cboe", "fmp"]


def test_param_provider_membership_falls_back_to_schema_keys():
    """No description tags → use per-provider schema extension keys."""
    from openbb_cli.dispatchers.openapi_schema import param_provider_membership

    schema = {
        "type": "string",
        "intrinio": {"choices": ["x"]},
    }
    membership = param_provider_membership(
        schema, None, providers_set={"cboe", "intrinio"}
    )
    assert membership == ["intrinio"]


def test_param_provider_membership_falls_back_to_title():
    """Last resort: schema title naming a single provider."""
    from openbb_cli.dispatchers.openapi_schema import param_provider_membership

    schema = {"type": "boolean", "title": "cboe"}
    membership = param_provider_membership(schema, None, providers_set={"cboe", "fmp"})
    assert membership == ["cboe"]


def test_param_provider_membership_returns_empty_for_neutral_param():
    """A param with no signal at all (e.g. the ``provider`` discriminator) is shared."""
    from openbb_cli.dispatchers.openapi_schema import param_provider_membership

    schema = {"type": "string", "title": "Provider"}
    membership = param_provider_membership(schema, None, providers_set={"cboe", "fmp"})
    assert membership == []


# --- Request body schema extraction ---


def test_extract_request_body_schema_returns_inlined_json_schema():
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schema

    spec = {}
    op = {
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"x": {"type": "integer"}},
                    }
                }
            }
        }
    }
    schema = extract_request_body_schema(spec, op)
    assert schema == {"type": "object", "properties": {"x": {"type": "integer"}}}


def test_extract_request_body_schema_dereferences_ref():
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schema

    spec = {
        "components": {
            "schemas": {
                "Body": {"type": "object", "properties": {"y": {"type": "string"}}}
            }
        }
    }
    op = {
        "requestBody": {
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/Body"}}
            }
        }
    }
    schema = extract_request_body_schema(spec, op)
    assert schema["properties"]["y"]["type"] == "string"


def test_extract_request_body_schema_returns_none_when_absent():
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schema

    assert extract_request_body_schema({}, {}) is None
    assert extract_request_body_schema({}, {"requestBody": {}}) is None


def test_extract_request_body_schemas_returns_per_content_type_map():
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schemas

    op = {
        "requestBody": {
            "content": {
                "application/json": {"schema": {"type": "object"}},
                "application/x-www-form-urlencoded": {"schema": {"type": "object"}},
            }
        }
    }
    schemas = extract_request_body_schemas({}, op)
    assert set(schemas) == {"application/json", "application/x-www-form-urlencoded"}


# --- Embedded spec extraction & fetch_openapi fallback ---


def test_find_matching_brace_returns_position_after_close():
    from openbb_cli.dispatchers.openapi_schema import _find_matching_brace

    text = '{"a": {"b": 1}, "c": 2}rest'
    end = _find_matching_brace(text, 0)
    assert text[:end] == '{"a": {"b": 1}, "c": 2}'


def test_find_matching_brace_returns_none_when_unbalanced():
    from openbb_cli.dispatchers.openapi_schema import _find_matching_brace

    assert _find_matching_brace('{"a": 1', 0) is None


def test_find_matching_brace_skips_braces_inside_strings():
    from openbb_cli.dispatchers.openapi_schema import _find_matching_brace

    text = '{"a": "{not-a-brace}"}'
    end = _find_matching_brace(text, 0)
    assert text[:end] == text  # whole thing


def test_find_matching_brace_handles_escaped_quotes():
    from openbb_cli.dispatchers.openapi_schema import _find_matching_brace

    text = r'{"a": "with \"quote\""}rest'
    end = _find_matching_brace(text, 0)
    assert text[:end].endswith('"}')


def test_find_matching_brace_returns_none_when_start_not_brace():
    from openbb_cli.dispatchers.openapi_schema import _find_matching_brace

    assert _find_matching_brace("no brace here", 0) is None


def test_extract_embedded_spec_finds_var_form():
    from openbb_cli.dispatchers.openapi_schema import _extract_embedded_spec

    html = '<html><script>var spec = {"openapi": "3.0.0", "paths": {}};</script></html>'
    spec = _extract_embedded_spec(html)
    assert spec is not None
    assert spec.get("openapi") == "3.0.0"


def test_extract_embedded_spec_finds_window_form():
    from openbb_cli.dispatchers.openapi_schema import _extract_embedded_spec

    html = 'window.spec = {"openapi": "3.0.0"};'
    spec = _extract_embedded_spec(html)
    assert spec is not None


def test_extract_embedded_spec_returns_none_when_object_unbalanced():
    from openbb_cli.dispatchers.openapi_schema import _extract_embedded_spec

    html = "var spec = {oops"
    assert _extract_embedded_spec(html) is None


def test_extract_embedded_spec_skips_non_openapi_objects():
    """A JS object that parses but isn't an OpenAPI spec is rejected."""
    from openbb_cli.dispatchers.openapi_schema import _extract_embedded_spec

    html = 'var spec = {"unrelated": 1};'
    assert _extract_embedded_spec(html) is None


def test_extract_embedded_spec_returns_none_when_no_marker():
    from openbb_cli.dispatchers.openapi_schema import _extract_embedded_spec

    assert _extract_embedded_spec("<html>boring page</html>") is None


def test_fetch_openapi_returns_parsed_json(monkeypatch):
    from openbb_cli.dispatchers import openapi_schema

    captured = {}

    class _R:
        status_code = 200
        text = '{"openapi": "3.0.0", "paths": {}}'
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            pass

    def fake_get(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return _R()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    spec = openapi_schema.fetch_openapi("https://api.example.com")
    assert spec["openapi"] == "3.0.0"
    assert captured["url"].endswith("/openapi.json")


def test_fetch_openapi_falls_back_to_landing_for_embedded(monkeypatch):
    """When ``/openapi.json`` doesn't parse, scrape the landing page for an embedded spec."""
    from openbb_cli.dispatchers import openapi_schema

    class _R:
        status_code = 404
        text = "<html>not here</html>"
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            raise openapi_schema.httpx.HTTPStatusError(
                "404", request=None, response=None
            )

    class _Landing:
        status_code = 200
        text = 'window.spec = {"openapi": "3.0.0", "paths": {}};'
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            pass

    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return _R() if "openapi.json" in url else _Landing()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    spec = openapi_schema.fetch_openapi("https://h.example.com")
    assert spec.get("openapi") == "3.0.0"
    # Tried the JSON endpoint first, then the landing page
    assert any("openapi.json" in u for u in calls)
    assert any(u.endswith("h.example.com/") for u in calls)


# --- Cycle / depth / fallback paths in deref + extractors ---


def test_resolve_ref_returns_empty_for_non_local_refs():
    from openbb_cli.dispatchers.openapi_schema import resolve_ref

    assert resolve_ref({}, "https://other-host/spec#/X") == {}


def test_resolve_ref_returns_empty_when_pointer_missing():
    from openbb_cli.dispatchers.openapi_schema import resolve_ref

    assert resolve_ref({"components": {}}, "#/components/schemas/Missing") == {}


def test_deref_parameter_breaks_ref_cycle():
    """A ``$ref`` cycle resolves to an empty dict instead of recursing forever."""
    from openbb_cli.dispatchers.openapi_schema import deref_parameter

    spec = {
        "components": {
            "parameters": {
                "a": {"$ref": "#/components/parameters/b"},
                "b": {"$ref": "#/components/parameters/a"},
            }
        }
    }
    out = deref_parameter(spec, {"$ref": "#/components/parameters/a"})
    assert out == {}


def test_deref_parameter_resolves_schema_ref():
    from openbb_cli.dispatchers.openapi_schema import deref_parameter

    spec = {"components": {"schemas": {"Limit": {"type": "integer", "minimum": 1}}}}
    out = deref_parameter(
        spec,
        {"name": "limit", "schema": {"$ref": "#/components/schemas/Limit"}},
    )
    assert out["schema"]["type"] == "integer"


def test_deref_schema_returns_node_when_max_depth_zero():
    from openbb_cli.dispatchers.openapi_schema import deref_schema

    sentinel = {"type": "object"}
    assert deref_schema({}, sentinel, max_depth=0) is sentinel


def test_deref_schema_marks_self_reference_with_ref_stub():
    """A schema whose nested ref points back to itself returns ``{"$ref": ref}``."""
    from openbb_cli.dispatchers.openapi_schema import deref_schema

    spec = {
        "components": {
            "schemas": {
                "Tree": {
                    "type": "object",
                    "properties": {"child": {"$ref": "#/components/schemas/Tree"}},
                }
            }
        }
    }
    out = deref_schema(spec, {"$ref": "#/components/schemas/Tree"})
    # The cycle is preserved as a $ref stub on the inner property
    assert out["properties"]["child"] == {"$ref": "#/components/schemas/Tree"}


def test_deref_schema_returns_node_when_ref_unresolvable():
    """Unresolvable ``$ref`` returns the original node, not None."""
    from openbb_cli.dispatchers.openapi_schema import deref_schema

    node = {"$ref": "#/components/schemas/Missing"}
    assert deref_schema({"components": {}}, node) == node


def test_deref_schema_recurses_into_lists():
    from openbb_cli.dispatchers.openapi_schema import deref_schema

    spec = {"components": {"schemas": {"X": {"type": "string"}}}}
    out = deref_schema(spec, [{"$ref": "#/components/schemas/X"}, "raw-string"])
    assert out == [{"type": "string"}, "raw-string"]


def test_deref_response_resolves_ref():
    from openbb_cli.dispatchers.openapi_schema import _deref_response

    spec = {"components": {"responses": {"OK": {"description": "ok", "content": {}}}}}
    out = _deref_response(spec, {"$ref": "#/components/responses/OK"})
    assert out["description"] == "ok"


# --- extract_response_schema branches ---


def test_extract_response_schema_falls_back_to_first_status():
    """If no preferred status (200/2XX/201/default) matches, use the first response."""
    from openbb_cli.dispatchers.openapi_schema import extract_response_schema

    op = {
        "responses": {
            "418": {"content": {"application/json": {"schema": {"type": "object"}}}}
        }
    }
    schema = extract_response_schema({}, op)
    assert schema == {"type": "object"}


def test_extract_response_schema_falls_back_to_first_content_type():
    """When no JSON content type is offered, the first content-type's schema is used."""
    from openbb_cli.dispatchers.openapi_schema import extract_response_schema

    op = {
        "responses": {"200": {"content": {"text/csv": {"schema": {"type": "string"}}}}}
    }
    schema = extract_response_schema({}, op)
    assert schema == {"type": "string"}


def test_extract_response_schema_returns_none_when_no_schema():
    from openbb_cli.dispatchers.openapi_schema import extract_response_schema

    op = {"responses": {"200": {"content": {"application/json": {}}}}}
    assert extract_response_schema({}, op) is None


def test_extract_response_schema_returns_none_when_no_responses():
    from openbb_cli.dispatchers.openapi_schema import extract_response_schema

    assert extract_response_schema({}, {}) is None


# --- extract_request_body_schema branches ---


def test_extract_request_body_schema_dereferences_request_body_ref():
    """The whole ``requestBody`` may itself be a $ref."""
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schema

    spec = {
        "components": {
            "requestBodies": {
                "Body": {
                    "content": {"application/json": {"schema": {"type": "object"}}}
                }
            }
        }
    }
    op = {"requestBody": {"$ref": "#/components/requestBodies/Body"}}
    schema = extract_request_body_schema(spec, op)
    assert schema == {"type": "object"}


def test_extract_request_body_schema_falls_back_to_first_content_type():
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schema

    op = {
        "requestBody": {
            "content": {"multipart/form-data": {"schema": {"type": "object"}}}
        }
    }
    schema = extract_request_body_schema({}, op)
    assert schema == {"type": "object"}


def test_extract_request_body_schema_returns_none_when_schema_missing():
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schema

    op = {"requestBody": {"content": {"application/json": {}}}}
    assert extract_request_body_schema({}, op) is None


def test_extract_request_body_schemas_dereferences_top_level_ref():
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schemas

    spec = {
        "components": {
            "requestBodies": {
                "B": {"content": {"application/json": {"schema": {"type": "object"}}}}
            }
        }
    }
    out = extract_request_body_schemas(
        spec, {"requestBody": {"$ref": "#/components/requestBodies/B"}}
    )
    assert out == {"application/json": {"type": "object"}}


def test_extract_request_body_schemas_skips_non_dict_media_entries():
    """Defensive: a media entry that isn't a dict gets dropped."""
    from openbb_cli.dispatchers.openapi_schema import extract_request_body_schemas

    op = {
        "requestBody": {
            "content": {
                "application/json": {"schema": {"type": "object"}},
                "broken": "not-a-dict",
            }
        }
    }
    out = extract_request_body_schemas({}, op)
    assert "application/json" in out
    assert "broken" not in out


# --- extract_response_schemas branches ---


def test_extract_response_schemas_skips_non_dict_responses():
    from openbb_cli.dispatchers.openapi_schema import extract_response_schemas

    op = {
        "responses": {
            "200": {"content": {"application/json": {"schema": {"type": "object"}}}},
            "default": "not-a-dict",
        }
    }
    out = extract_response_schemas({}, op)
    assert "200" in out
    assert "default" not in out


# --- _extract_embedded_spec marker variants ---


def test_extract_embedded_spec_skips_whitespace_after_marker():
    """Whitespace and newlines between marker and ``{`` are tolerated."""
    from openbb_cli.dispatchers.openapi_schema import _extract_embedded_spec

    html = 'var spec =   \n   {"openapi": "3.0.0"};'
    spec = _extract_embedded_spec(html)
    assert spec is not None


def test_extract_embedded_spec_continues_past_invalid_json_match():
    """A marker followed by invalid JSON doesn't abort — keeps scanning."""
    from openbb_cli.dispatchers.openapi_schema import _extract_embedded_spec

    html = 'var spec = {bad-json};\nwindow.spec = {"openapi": "3.0.0"};'
    spec = _extract_embedded_spec(html)
    assert spec is not None
    assert spec["openapi"] == "3.0.0"


# --- fetch_openapi explicit path / landing fallback raise ---


def test_fetch_openapi_explicit_path_calls_target_url(monkeypatch):
    """An explicit ``path`` is honored — fetched URL is ``base_url + path``."""
    from openbb_cli.dispatchers import openapi_schema

    captured: dict[str, str] = {}

    class _R:
        status_code = 200
        text = '{"openapi": "3.0.0"}'
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            pass

    def fake_get(url, **kw):
        captured["url"] = url
        return _R()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    spec = openapi_schema.fetch_openapi("http://h", path="/static/openapi.yml")
    assert spec["openapi"] == "3.0.0"
    assert captured["url"].endswith("/static/openapi.yml")


def test_fetch_openapi_raises_when_no_embedded_spec_and_landing_succeeds(monkeypatch):
    """No-marker landing page → re-raise the original JSON-fetch error."""
    from openbb_cli.dispatchers import openapi_schema

    class _Bad:
        status_code = 404
        text = "<html>nope</html>"
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            raise openapi_schema.httpx.HTTPStatusError(
                "404", request=None, response=None
            )

    class _Landing:
        status_code = 200
        text = "<html>boring</html>"
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            pass

    def fake_get(url, **kw):
        return _Bad() if "openapi.json" in url else _Landing()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    with pytest.raises(openapi_schema.httpx.HTTPStatusError):
        openapi_schema.fetch_openapi("http://h")


# --- parse_provider_sections empty section ---


def test_parse_provider_sections_skips_empty_sections():
    """Whitespace-only sections (after a trailing separator) are skipped."""
    from openbb_cli.dispatchers.openapi_schema import parse_provider_sections

    text = "Real. (provider: cboe);\n   ;\n    "
    tagged, has_untagged = parse_provider_sections(text)
    assert tagged == {"cboe"}
    assert has_untagged is False


def test_extract_response_schema_returns_none_when_no_schema_in_any_content_type():
    """Content has entries but none expose a schema → None, not crash."""
    from openbb_cli.dispatchers.openapi_schema import extract_response_schema

    op = {
        "responses": {
            "200": {
                "content": {
                    "text/csv": "not-a-dict",
                    "application/x-protobuf": {},
                }
            }
        }
    }
    assert extract_response_schema({}, op) is None


def test_extract_response_schemas_skips_non_dict_media():
    """Inside a per-content-type loop, non-dict media entries are dropped."""
    from openbb_cli.dispatchers.openapi_schema import extract_response_schemas

    op = {
        "responses": {
            "200": {
                "content": {
                    "application/json": {"schema": {"type": "object"}},
                    "broken": "not-a-dict",
                }
            }
        }
    }
    out = extract_response_schemas({}, op)
    assert "application/json" in out["200"]
    assert "broken" not in out["200"]


def test_fetch_openapi_falls_through_to_raise_when_landing_has_no_embedded(monkeypatch):
    """Landing page with no embedded spec re-raises the original openapi.json error."""
    from openbb_cli.dispatchers import openapi_schema

    class _R:
        status_code = 500
        text = "internal"
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            raise openapi_schema.httpx.HTTPStatusError(
                "500", request=None, response=None
            )

    class _Landing:
        status_code = 200
        text = "<html>nothing useful</html>"
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            pass

    def fake_get(url, **kw):
        return _R() if "openapi.json" in url else _Landing()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    with pytest.raises(openapi_schema.httpx.HTTPStatusError):
        openapi_schema.fetch_openapi("http://h")


def test_fetch_openapi_swallows_initial_parse_error_and_scrapes_landing(monkeypatch):
    """200 with unparsable body → fall through to landing-page scrape."""
    from openbb_cli.dispatchers import openapi_schema

    class _Bad:
        status_code = 200
        text = "{not-valid-json"  # leading { → JSON-only path → JSONDecodeError
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            pass

    class _Landing:
        status_code = 200
        text = 'window.spec = {"openapi": "3.0.0", "paths": {}};'
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            pass

    def fake_get(url, **kw):
        return _Bad() if "openapi.json" in url else _Landing()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    spec = openapi_schema.fetch_openapi("http://h")
    assert spec.get("openapi") == "3.0.0"


def test_fetch_openapi_with_explicit_path_reparses_and_raises(monkeypatch):
    """Explicit ``path`` + unparsable body re-raises after the initial swallow."""
    from openbb_cli.dispatchers import openapi_schema

    class _Bad:
        status_code = 200
        text = "{not-valid-json"
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(openapi_schema.httpx, "get", lambda url, **kw: _Bad())
    with pytest.raises((ValueError,)):  # JSONDecodeError is a ValueError subclass
        openapi_schema.fetch_openapi("http://h", path="/custom.json")


def test_fetch_openapi_final_parse_attempt_runs_when_landing_empty(monkeypatch):
    """Initial parse fails, landing has no embedded spec, no explicit path:
    re-attempt the original parse — which raises again, propagating the error."""
    from openbb_cli.dispatchers import openapi_schema

    class _Bad:
        status_code = 200
        text = "{not-valid-json"
        headers = {"content-type": "application/json"}

        def raise_for_status(self):
            pass

    class _Landing:
        status_code = 200
        text = "<html>nothing relevant</html>"
        headers = {"content-type": "text/html"}

        def raise_for_status(self):
            pass

    def fake_get(url, **kw):
        return _Bad() if "openapi.json" in url else _Landing()

    monkeypatch.setattr(openapi_schema.httpx, "get", fake_get)
    with pytest.raises((ValueError,)):
        openapi_schema.fetch_openapi("http://h")
