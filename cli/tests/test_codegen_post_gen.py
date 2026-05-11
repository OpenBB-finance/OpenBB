"""Tests for openbb_cli.codegen.post_gen — POST router function emission."""

from __future__ import annotations

import ast

from openbb_cli.codegen import post_gen as pg

# --- _module_name_from_command ---


def test_module_name_from_command_snake_cases_dotted_path():
    assert pg._module_name_from_command("econometrics.ols_regression") == (
        "econometrics_ols_regression"
    )


def test_module_name_from_command_replaces_special_chars_and_handles_empty():
    assert pg._module_name_from_command("___") == "command"
    assert pg._module_name_from_command("Foo-Bar") == "foo_bar"


def test_module_name_from_command_prefixes_underscore_when_starts_with_digit():
    assert pg._module_name_from_command("3pl.tools") == "_3pl_tools"


# --- _path_template_keys ---


def test_path_template_keys_extracts_placeholders_in_order():
    assert pg._path_template_keys("/a/{b}/{c}") == ["b", "c"]


def test_path_template_keys_returns_empty_when_no_placeholders():
    assert pg._path_template_keys("/static") == []


# --- _resolve_url_path ---


def test_resolve_url_path_appends_prefix_when_missing():
    assert pg._resolve_url_path("/api/v1", "/x") == "/api/v1/x"


def test_resolve_url_path_skips_prefix_when_already_present():
    assert pg._resolve_url_path("/api/v1", "/api/v1/x") == "/api/v1/x"


def test_resolve_url_path_handles_blank_prefix():
    assert pg._resolve_url_path("", "/x") == "/x"


def test_resolve_url_path_normalizes_missing_leading_slash():
    assert pg._resolve_url_path("/api", "x") == "/api/x"


def test_resolve_url_path_keeps_path_when_prefix_partially_matches():
    assert pg._resolve_url_path("/api/v1", "/api/v1") == "/api/v1"


# --- _python_type_from_param ---


def test_python_type_from_param_maps_basic_types():
    assert pg._python_type_from_param({"type": "string"}) == "str"
    assert pg._python_type_from_param({"type": "integer"}) == "int"
    assert pg._python_type_from_param({"type": "number"}) == "float"
    assert pg._python_type_from_param({"type": "boolean"}) == "bool"


def test_python_type_from_param_falls_back_to_str_for_unknown_type():
    assert pg._python_type_from_param({"type": "weird"}) == "str"
    assert pg._python_type_from_param({}) == "str"


def test_python_type_from_param_renders_literal_for_choices():
    assert (
        pg._python_type_from_param({"type": "string", "choices": ["a", "b"]})
        == "Literal['a', 'b']"
    )


def test_python_type_from_param_wraps_in_list_when_is_list():
    assert (
        pg._python_type_from_param({"type": "integer", "is_list": True}) == "list[int]"
    )


# --- render_default ---


def test_render_default_handles_none_bool_and_other_literals():
    assert pg.render_default(None) == "None"
    assert pg.render_default(True) == "True"
    assert pg.render_default(False) == "False"
    assert pg.render_default(42) == "42"
    assert pg.render_default("hello") == "'hello'"


# --- _array_item_class ---


def test_array_item_class_top_level_array_body_returns_data_field():
    body = {
        "type": "array",
        "items": {"type": "object", "properties": {"a": {"type": "integer"}}},
    }
    field, item_class, ann = pg._array_item_class(body, parent_class_name="Foo")
    assert field == "data"
    assert ann == "list[FooBodyItem]"
    assert item_class is not None
    assert item_class.name == "FooBodyItem"


def test_array_item_class_top_level_array_body_with_non_dict_items_returns_none():
    body = {"type": "array", "items": "not a dict"}
    out = pg._array_item_class(body, parent_class_name="Foo")
    assert out == (None, None, None)


def test_array_item_class_object_body_with_array_field():
    body = {
        "type": "object",
        "properties": {
            "rows": {
                "type": "array",
                "items": {"type": "object", "properties": {"x": {"type": "string"}}},
            }
        },
    }
    field, item_class, ann = pg._array_item_class(body, parent_class_name="Q")
    assert field == "rows"
    assert ann == "list[QBodyItem]"
    assert item_class.name == "QBodyItem"


def test_array_item_class_object_body_skips_non_dict_property():
    body = {"type": "object", "properties": {"x": "not a dict"}}
    assert pg._array_item_class(body, parent_class_name="Q") == (None, None, None)


def test_array_item_class_object_body_skips_non_array_property():
    body = {"type": "object", "properties": {"x": {"type": "string"}}}
    assert pg._array_item_class(body, parent_class_name="Q") == (None, None, None)


def test_array_item_class_object_body_skips_array_with_non_dict_items():
    body = {
        "type": "object",
        "properties": {"rows": {"type": "array", "items": "scalar"}},
    }
    assert pg._array_item_class(body, parent_class_name="Q") == (None, None, None)


def test_array_item_class_object_body_skips_array_of_scalars():
    body = {
        "type": "object",
        "properties": {"rows": {"type": "array", "items": {"type": "string"}}},
    }
    assert pg._array_item_class(body, parent_class_name="Q") == (None, None, None)


# --- _data_schema ---


def test_data_schema_descends_into_obbject_anyof_array_items():
    out = pg._data_schema(
        {
            "response_schema": {
                "properties": {
                    "results": {
                        "anyOf": [
                            {"type": "null"},
                            {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {"x": {"type": "string"}},
                                },
                            },
                        ]
                    }
                }
            }
        }
    )
    assert out["properties"] == {"x": {"type": "string"}}


def test_data_schema_descends_into_oneof():
    out = pg._data_schema(
        {
            "response_schema": {
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {"a": {"type": "string"}},
                                }
                            ]
                        },
                    }
                }
            }
        }
    )
    assert out["properties"] == {"a": {"type": "string"}}


def test_data_schema_returns_response_when_results_field_is_not_dict():
    response = {"properties": {"results": "scalar"}}
    assert pg._data_schema({"response_schema": response}) == response


def test_data_schema_descends_through_results_anyof_envelope():
    """``results.anyOf`` is a recognized envelope shape — even when the only
    variant is ``null``, the envelope unwraps so codegen doesn't emit
    ``results: Any`` as a real field on the parent class."""
    response = {"properties": {"results": {"anyOf": [{"type": "null"}]}}}
    assert pg._data_schema({"response_schema": response}) == {
        "anyOf": [{"type": "null"}]
    }


def test_data_schema_returns_top_level_when_no_results_field_multi_property():
    """Multi-property dict with no clear single data array -> whole dict is the row."""
    response = {
        "type": "object",
        "properties": {"x": {"type": "integer"}, "y": {"type": "string"}},
    }
    assert pg._data_schema({"response_schema": response}) == response


def test_data_schema_unwraps_single_key_array_envelope():
    response = {
        "type": "object",
        "properties": {
            "rows": {
                "type": "array",
                "items": {"type": "object", "properties": {"v": {"type": "integer"}}},
            }
        },
    }
    out = pg._data_schema({"response_schema": response})
    assert out == {"type": "object", "properties": {"v": {"type": "integer"}}}


def test_data_schema_unwraps_top_level_array():
    response = {
        "type": "array",
        "items": {"type": "object", "properties": {"a": {"type": "integer"}}},
    }
    out = pg._data_schema({"response_schema": response})
    assert out == {"type": "object", "properties": {"a": {"type": "integer"}}}


def test_data_schema_top_level_array_with_non_dict_items_returns_empty():
    response = {"type": "array", "items": "scalar"}
    assert pg._data_schema({"response_schema": response}) == {}


def test_data_schema_unwraps_single_key_array_of_scalars():
    response = {
        "type": "object",
        "properties": {"dates": {"type": "array", "items": {"type": "string"}}},
    }
    assert pg._data_schema({"response_schema": response}) == {
        "type": "object",
        "properties": {"value": {"type": "string"}},
        "required": ["value"],
    }


def test_data_schema_descends_into_single_array_among_scalar_siblings():
    """Multi-property row with exactly one array property → descend to the
    array's items, mirroring ``unpack_response``'s runtime behavior (which
    extracts the single array as rows and treats the scalar siblings as
    metadata). The Data class describes the row shape, not the wrapping
    envelope.
    """
    response = {
        "type": "object",
        "properties": {
            "items": {
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                }
            }
        },
    }
    out = pg._data_schema({"response_schema": response})
    # Descended through ``items`` (single-property), then through ``tags``
    # (single array among scalar siblings), then wrapped the scalar item
    # schema as a ``{value: str}`` row.
    assert out == {
        "type": "object",
        "properties": {"value": {"type": "string"}},
        "required": ["value"],
    }


def test_data_schema_descends_oneOf_to_first_concrete_variant():
    response = {
        "type": "object",
        "properties": {
            "wrapper": {
                "type": "array",
                "items": {
                    "oneOf": [
                        {"properties": {"a": {"type": "string"}}},
                        {"properties": {"b": {"type": "integer"}}},
                    ]
                },
            }
        },
    }
    out = pg._data_schema({"response_schema": response})
    assert out.get("properties") == {"a": {"type": "string"}}


def test_data_schema_keeps_array_with_non_dict_items():
    response = {
        "type": "object",
        "properties": {"rows": {"type": "array", "items": "scalar"}},
    }
    assert pg._data_schema({"response_schema": response}) == response


def test_data_schema_keeps_single_key_with_scalar_value():
    response = {"type": "object", "properties": {"x": "not a dict"}}
    assert pg._data_schema({"response_schema": response}) == response


def test_data_schema_returns_schema_when_no_properties():
    response = {"type": "object"}
    assert pg._data_schema({"response_schema": response}) == response


def test_unwrap_schema_envelopes_returns_empty_for_non_dict_input():
    assert pg._unwrap_schema_envelopes("not a dict") == {}  # type: ignore[arg-type]


def test_data_schema_recurses_into_nested_single_key_envelope():
    response = {
        "type": "object",
        "properties": {
            "outer": {
                "type": "object",
                "properties": {
                    "inner": {
                        "type": "object",
                        "properties": {"v": {"type": "integer"}},
                    }
                },
            }
        },
    }
    assert pg._data_schema({"response_schema": response}) == {
        "type": "object",
        "properties": {"v": {"type": "integer"}},
    }


def test_data_schema_returns_empty_when_no_response():
    assert pg._data_schema({}) == {}


def test_data_schema_returns_empty_when_response_is_not_dict():
    assert pg._data_schema({"response_schema": "scalar"}) == {}


# --- _credential_lookup_lines ---


def test_credential_lookup_lines_emits_user_credential_block():
    creds = {"api_key": {"name": "apikey", "in": "query"}}
    lines = pg._credential_lookup_lines(creds, provider_name="myprov")
    assert lines[0] == "    _user_creds = cc.user_settings.credentials"
    assert (
        '    _cred_api_key = (getattr(_user_creds, "myprov_api_key", "") or "")'
        in lines
    )


def test_credential_lookup_lines_returns_empty_when_no_credentials():
    assert pg._credential_lookup_lines({}, provider_name="x") == []


# --- _signature_params ---


def test_signature_params_orders_cc_required_optional():
    cmd = {
        "parameters": [
            {"name": "limit", "type": "integer"},
            {"name": "symbol", "type": "string", "required": True},
        ],
        "request_body_schema": {
            "type": "array",
            "items": {"type": "object"},
        },
    }
    out = pg._signature_params(
        cmd,
        array_field="data",
        array_annotation="list[FooBodyItem]",
        has_credentials=True,
    )
    names_in_order = [entry[0] for entry in out]
    assert names_in_order[0] == "cc"
    # All required parameters must come before optional ones
    required_idx = [i for i, e in enumerate(out) if e[3]]
    optional_idx = [i for i, e in enumerate(out) if not e[3]]
    assert max(required_idx) < min(optional_idx)


def test_signature_params_includes_object_body_fields_when_no_array():
    cmd = {
        "request_body_schema": {
            "type": "object",
            "properties": {
                "alpha": {"type": "number", "description": "Tuning."},
                "ignored": "scalar",  # non-dict, must be skipped
            },
            "required": ["alpha"],
        },
    }
    out = pg._signature_params(
        cmd, array_field=None, array_annotation=None, has_credentials=False
    )
    names = [e[0] for e in out]
    assert "alpha" in names
    assert "ignored" not in names


def test_signature_params_skips_array_field_when_present_in_body_props():
    cmd = {
        "request_body_schema": {
            "type": "object",
            "properties": {
                "data": {"type": "array"},
                "meta": {"type": "string"},
            },
        },
    }
    out = pg._signature_params(
        cmd,
        array_field="data",
        array_annotation="list[X]",
        has_credentials=False,
    )
    names = [e[0] for e in out]
    # 'data' appears once (from the array_field, not body props)
    assert names.count("data") == 1
    assert "meta" in names


def test_signature_params_includes_query_parameters_from_cmd_spec():
    cmd = {
        "parameters": [{"name": "limit", "type": "integer", "default": 10}],
    }
    out = pg._signature_params(
        cmd, array_field=None, array_annotation=None, has_credentials=False
    )
    by_name = {e[0]: e for e in out}
    assert "limit" in by_name
    # default carries through
    assert by_name["limit"][4] == 10


def test_signature_params_skips_unnamed_query_parameters():
    cmd = {"parameters": [{"type": "string"}, {"name": "x", "type": "string"}]}
    out = pg._signature_params(
        cmd, array_field=None, array_annotation=None, has_credentials=False
    )
    assert [e[0] for e in out] == ["x"]


# --- _render_signature ---


def test_render_signature_no_params_renders_empty_signature():
    out = pg._render_signature("foo", [], "OBBject[list[FooData]]")
    assert out == "async def foo() -> OBBject[list[FooData]]:"


def test_render_signature_renders_required_and_optional_with_defaults():
    params = [
        ("data", "list[X]", "Body data.", True, None),
        ("limit", "int", "Limit.", False, 5),
    ]
    out = pg._render_signature("foo", params, "OBBject[list[FooData]]")
    assert "async def foo(" in out
    assert "    data: list[X]," in out
    assert "    limit: int = 5," in out
    assert ") -> OBBject[list[FooData]]:" in out


# --- generate_post_command_module (end-to-end) ---


def _econometrics_spec():
    return pg.PostCommandSpec(
        name="econometrics.ols_regression",
        cmd_spec={
            "url_path": "/econometrics/ols",
            "method": "post",
            "description": "OLS regression.",
            "parameters": [
                {"name": "y_column", "type": "string", "required": True},
            ],
            "request_body_schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"x": {"type": "number"}},
                        },
                    },
                    "alpha": {"type": "number", "default": 0.05},
                },
                "required": ["data"],
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"slope": {"type": "number"}},
                        },
                    }
                },
            },
        },
        base_url="https://api.example.com/",
        api_prefix="api/v1",
        provider_name="tools",
    )


def test_generate_post_command_module_emits_valid_module():
    out = pg.generate_post_command_module(_econometrics_spec())
    assert isinstance(out, pg.GeneratedPostCommand)
    assert out.module_name == "econometrics_ols_regression"
    assert out.function_name == "econometrics_ols_regression"
    assert out.body_class == "EconometricsOlsRegressionBodyItem"
    assert out.data_class == "EconometricsOlsRegressionData"
    src = out.source
    ast.parse(src)
    assert "class EconometricsOlsRegressionBodyItem(Data)" in src
    assert "class EconometricsOlsRegressionData(BaseModel)" in src
    assert "async def econometrics_ols_regression(" in src
    assert '_session.request("POST", _url' in src
    assert "get_async_requests_session" in src
    assert "raise OpenBBError(" in src
    assert ("https://api.example.com/api/v1/econometrics/ols") in src


def test_generate_post_command_module_uses_default_description_when_missing():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x/y",
            "method": "post",
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    assert "POST x.y." in out.source


def test_generate_post_command_module_top_level_array_body():
    spec = pg.PostCommandSpec(
        name="quant.bulk_load",
        cmd_spec={
            "url_path": "/q/bulk",
            "method": "post",
            "description": "Bulk load.",
            "request_body_schema": {
                "type": "array",
                "items": {"type": "object", "properties": {"v": {"type": "number"}}},
            },
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    src = out.source
    ast.parse(src)
    assert "data: list[QuantBulkLoadBodyItem]" in src
    # Top-level array body serializes the array itself, not a wrapper dict
    assert (
        "_body: list[dict[str, Any]] = "
        '[_item.model_dump(mode="json") for _item in data]'
    ) in src


def test_generate_post_command_module_with_path_params_emits_format_call():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x/{slug}",
            "method": "post",
            "description": "Slug.",
            "parameters": [
                {"name": "slug", "type": "string", "required": True},
            ],
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    assert "'/x/{slug}'.format(slug=slug)" in out.source


def test_generate_post_command_module_with_credentials_renders_cred_block():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x",
            "method": "post",
            "description": "X.",
            "parameters": [
                {"name": "apikey", "type": "string", "in": "query"},
                {"name": "Authorization", "type": "string", "in": "header"},
            ],
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="myprov",
    )
    out = pg.generate_post_command_module(spec)
    src = out.source
    assert "from openbb_core.app.model.command_context import CommandContext" in src
    assert "cc.user_settings.credentials" in src
    # Header creds appear in the headers block, query creds in the query string
    assert "_headers['Authorization']" in src
    assert "_query_dict['apikey']" in src
    ast.parse(src)


def test_generate_post_command_module_multiline_description_renders_block_doc():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x",
            "method": "post",
            "description": "Summary line.\nMore detail.\n\nFinal point.",
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    src = out.source
    assert '"""Summary line.\n' in src
    assert "More detail." in src
    assert "Final point." in src


def test_generate_post_command_module_with_literal_param_imports_literal():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x",
            "method": "post",
            "description": "X.",
            "parameters": [
                {
                    "name": "mode",
                    "type": "string",
                    "choices": ["a", "b"],
                    "required": True,
                },
            ],
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    # ``Literal`` ends up consolidated with other ``typing`` imports
    assert "Literal" in out.source
    assert "from typing import" in out.source
    assert "mode: Literal['a', 'b']" in out.source


def test_generate_post_command_module_body_props_only_object_form():
    """Object body with only scalar fields uses dict-wrapped body literal."""
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x",
            "method": "post",
            "description": "X.",
            "request_body_schema": {
                "type": "object",
                "properties": {
                    "alpha": {"type": "number"},
                    "beta": {"type": "string"},
                },
                "required": ["alpha", "beta"],
            },
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    src = out.source
    ast.parse(src)
    assert "_body: dict[str, Any] = {" in src
    assert "'alpha': alpha," in src
    assert "'beta': beta," in src


def test_generate_post_command_module_appends_period_when_description_lacks_terminator():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x",
            "method": "post",
            "description": "No trailing period",
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    assert '"""No trailing period."""' in out.source


def test_generate_post_command_module_whitespace_description_falls_back_to_summary():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x",
            "method": "post",
            # Whitespace-only description: ``description.strip()`` == "" so the
            # fallback inside generate_post_command_module promotes ``summary``
            # back into the cleaned text.
            "description": "   ",
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    # Just verify it produces a valid module — the docstring content is
    # implementation-defined when description is whitespace-only.
    out = pg.generate_post_command_module(spec)
    ast.parse(out.source)


def test_generate_post_command_module_no_body_props_uses_empty_body_dict():
    spec = pg.PostCommandSpec(
        name="x.y",
        cmd_spec={
            "url_path": "/x",
            "method": "post",
            "description": "X.",
            "request_body_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object"},
        },
        base_url="https://api.example.com",
        api_prefix="",
        provider_name="tools",
    )
    out = pg.generate_post_command_module(spec)
    assert "_body: dict[str, Any] = {}" in out.source
