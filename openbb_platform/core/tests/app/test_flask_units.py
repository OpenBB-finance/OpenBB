"""Branch-coverage tests for the Flask utils package."""

import importlib.util

import pytest

from openbb_core.app.utils.flask import (
    ast_analysis as aa,
    detection,
)
from openbb_core.app.utils.flask.docstrings import parse_docstring
from openbb_core.app.utils.flask.introspector import (
    FlaskIntrospector,
    _any_enum,
    _swagger2_to_openapi3,
)
from openbb_core.app.utils.flask.openapi import OpenAPISpecGenerator
from openbb_core.app.utils.flask.registry import FlaskMountRegistry
from openbb_core.app.utils.flask.types import OperationInfo, ParamInfo, RouteInfo

FLASK_AVAILABLE = importlib.util.find_spec("flask") is not None


@pytest.fixture(autouse=True)
def _reset_registry():
    FlaskMountRegistry.reset()
    yield
    FlaskMountRegistry.reset()


def test_detection_helpers():
    assert detection.flask_available() is FLASK_AVAILABLE
    assert detection.is_flask_app(object()) is False


def test_is_flask_app_true_via_mro():
    class _StubFlask:
        pass

    _StubFlask.__module__ = "flask.app"
    _StubFlask.__qualname__ = "Flask"
    assert detection.is_flask_app(_StubFlask()) is True


def test_package_lazy_exports():
    import openbb_core.app.utils.flask as pkg

    assert pkg.FlaskMountRegistry is FlaskMountRegistry
    assert callable(pkg.is_flask_app)
    assert callable(pkg.flask_available)
    assert callable(pkg.mount_flask_extensions)
    assert callable(pkg.merge_flask_openapi)
    with pytest.raises(AttributeError):
        _ = pkg.does_not_exist


def test_analyze_unreadable_source_is_partial():
    assert aa.analyze_view_source(len) == ([], [], None, True)


def test_analyze_syntax_error_is_partial(monkeypatch):
    monkeypatch.setattr(aa, "getsource", lambda _f: "def (: bad")
    assert aa.analyze_view_source(lambda: None) == ([], [], None, True)


def _v_form():
    from flask import request

    request.form.get("a")
    return request.form["b"]


def test_ast_form_get_and_subscript():
    _, _, body, _ = aa.analyze_view_source(_v_form)
    assert body is not None
    assert body.media_type == "application/x-www-form-urlencoded"
    assert {"a", "b"} <= set(body.schema["properties"])


def _v_files():
    from flask import request

    return request.files["f"]


def test_ast_files_multipart():
    _, _, body, _ = aa.analyze_view_source(_v_files)
    assert body is not None
    assert body.media_type == "multipart/form-data"
    assert body.schema["properties"]["f"] == {"type": "string", "format": "binary"}


def _v_data():
    from flask import request

    return request.data


def test_ast_data_binary():
    _, _, body, _ = aa.analyze_view_source(_v_data)
    assert body is not None
    assert body.media_type == "application/octet-stream"


def _v_values():
    from flask import request

    return request.values.get("x", type=float)


def test_ast_values_typed_query():
    query, _, _, _ = aa.analyze_view_source(_v_values)
    assert {p.name: p.schema["type"] for p in query}["x"] == "number"


def _v_json_binding():
    from flask import request

    data = request.get_json()
    return data["k"]


def test_ast_json_binding_subscript():
    _, _, body, _ = aa.analyze_view_source(_v_json_binding)
    assert body is not None
    assert body.media_type == "application/json"
    assert "k" in body.schema["properties"]


def _v_args_binding():
    from flask import request

    a = request.args
    return a.get("z")


def test_ast_args_binding():
    query, _, _, _ = aa.analyze_view_source(_v_args_binding)
    assert {p.name for p in query} == {"z"}


def _v_header_subscript():
    from flask import request

    return request.headers["X-Trace"]


def test_ast_header_subscript():
    _, headers, _, _ = aa.analyze_view_source(_v_header_subscript)
    assert {h.name for h in headers} == {"X-Trace"}


def _v_default_keyword():
    from flask import request

    return request.args.get("n", default="0")


def test_ast_default_keyword_example():
    query, _, _, _ = aa.analyze_view_source(_v_default_keyword)
    assert {p.name: p.example for p in query}["n"] == "0"


def _v_dynamic_key():
    from flask import request

    key = "x"
    return request.args.get(key)


def test_ast_dynamic_key_is_partial():
    _, _, _, partial = aa.analyze_view_source(_v_dynamic_key)
    assert partial is True


def _v_to_dict_on_binding():
    from flask import request

    a = request.args
    return a.to_dict()


def test_ast_to_dict_on_binding_partial():
    _, _, _, partial = aa.analyze_view_source(_v_to_dict_on_binding)
    assert partial is True


def test_parse_docstring_empty_inputs():
    assert parse_docstring(None) == (None, None, {})
    assert parse_docstring("   ") == (None, None, {})


def test_parse_docstring_no_param_block():
    summary, description, params = parse_docstring("Only a summary line.")
    assert summary == "Only a summary line."
    assert description is None
    assert params == {}


def test_parse_numpy_multiline_description():
    _, _, params = parse_docstring(
        "Title.\n\nParameters\n----------\nx\n    Line one\n    line two.\n"
    )
    assert params["x"] == "Line one line two."


def test_converter_schema_defaults():
    assert FlaskIntrospector._converter_schema(None, "/x", "a") == {"type": "string"}

    class Unknown:
        pass

    assert FlaskIntrospector._converter_schema(Unknown(), "/x", "a") == {
        "type": "string"
    }


def test_any_enum_no_match_returns_empty():
    assert _any_enum("/x/<int:y>", "y") == []


def test_swagger2_to_openapi3_v3_passthrough():
    spec = _swagger2_to_openapi3(
        {"openapi": "3.1.0", "paths": {"/y": {}}, "components": {"schemas": {"N": {}}}}
    )
    assert spec["paths"] == {"/y": {}}
    assert spec["components"]["schemas"] == {"N": {}}


def test_swagger2_to_openapi3_v2_definitions():
    spec = _swagger2_to_openapi3(
        {
            "swagger": "2.0",
            "paths": {"/z": {}},
            "definitions": {"M": {"type": "object"}},
        }
    )
    assert spec["components"]["schemas"] == {"M": {"type": "object"}}


def test_responses_pydantic_model_ref():
    from pydantic import BaseModel

    class Row(BaseModel):
        x: int

    def view() -> Row:
        return Row(x=1)

    components: dict = {}
    responses = FlaskIntrospector._responses(view, components)
    schema = responses["200"]["content"]["application/json"]["schema"]
    assert schema == {"$ref": "#/components/schemas/Row"}
    assert "Row" in components


def test_registry_get_names_and_security_aggregation():
    assert FlaskMountRegistry.get("missing") is None
    FlaskMountRegistry.register(
        "a",
        {"/p": {"get": {}}},
        {"schemas": {"S": {}}, "securitySchemes": {"bearerAuth": {"type": "http"}}},
    )
    FlaskMountRegistry.register("b", {"/p": {"get": {}}}, {"schemas": {"S": {}}})
    assert set(FlaskMountRegistry.names()) == {"a", "b"}
    merged = FlaskMountRegistry.aggregate("/api/v1")
    assert "bearerAuth" in merged["components"]["securitySchemes"]
    assert "S" in merged["components"]["schemas"]
    assert "b__S" in merged["components"]["schemas"]


def test_openapi_generator_components_and_optional_fields():
    route = RouteInfo(
        path="/x",
        operations=[
            OperationInfo(
                method="get",
                operation_id="x",
                description="A description.",
                parameters=[
                    ParamInfo(
                        "q",
                        "query",
                        {"type": "string"},
                        description="d",
                        example="e",
                    )
                ],
            )
        ],
    )
    spec = OpenAPISpecGenerator([route], {"M": {"type": "object"}}).generate()
    operation = spec["paths"]["/x"]["get"]
    assert operation["description"] == "A description."
    param = operation["parameters"][0]
    assert param["description"] == "d"
    assert param["example"] == "e"
    assert spec["components"]["schemas"] == {"M": {"type": "object"}}


def test_openapi_generator_api_key_security():
    route = RouteInfo(
        path="/x",
        operations=[
            OperationInfo(
                method="get",
                operation_id="x",
                parameters=[ParamInfo("X-API-Key", "header", {"type": "string"})],
            )
        ],
    )
    spec = OpenAPISpecGenerator([route]).generate()
    operation = spec["paths"]["/x"]["get"]
    assert {"apiKeyAuth": []} in operation["security"]
    assert spec["components"]["securitySchemes"]["apiKeyAuth"]["in"] == "header"


def test_widget_config_absent_when_no_id_or_author_config():
    route = RouteInfo(
        path="/x", operations=[OperationInfo(method="get", operation_id="x")]
    )
    operation = OpenAPISpecGenerator([route]).generate()["paths"]["/x"]["get"]
    assert "widget_config" not in operation


def test_partial_operation_marked_in_openapi():
    route = RouteInfo(
        path="/x",
        operations=[OperationInfo(method="get", operation_id="x", partial=True)],
    )
    operation = OpenAPISpecGenerator([route]).generate()["paths"]["/x"]["get"]
    assert operation["x-openbb-introspection"] == "partial"


def test_mount_flask_extensions_no_apps_is_noop():
    from unittest.mock import PropertyMock, patch

    from fastapi import FastAPI

    from openbb_core.app.utils.flask import mount_flask_extensions

    with patch(
        "openbb_core.app.extension_loader.ExtensionLoader.flask_objects",
        new_callable=PropertyMock,
        return_value={},
    ):
        api = FastAPI()
        mount_flask_extensions(api, "/api/v1")
    assert FlaskMountRegistry.names() == []


def test_merge_flask_openapi_noop_when_empty():
    from openbb_core.app.utils.flask import merge_flask_openapi

    schema = {"paths": {"/keep": {}}, "components": {}}
    result = merge_flask_openapi(schema, "/api/v1")
    assert result["paths"] == {"/keep": {}}


def test_merge_flask_openapi_adds_registered_paths():
    from openbb_core.app.utils.flask import merge_flask_openapi

    FlaskMountRegistry.register("demo", {"/data": {"get": {}}}, {"schemas": {"S": {}}})
    schema = {"paths": {"/keep": {}}, "components": {"schemas": {"K": {}}}}
    result = merge_flask_openapi(schema, "/api/v1")
    assert "/keep" in result["paths"]
    assert "/api/v1/demo/data" in result["paths"]
    assert "S" in result["components"]["schemas"]


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_register_openapi_survives_introspection_error(monkeypatch):
    from flask import Flask

    from openbb_core.app.utils.flask import introspector, loader

    monkeypatch.setattr(
        introspector.FlaskIntrospector,
        "introspect",
        lambda self: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    app = Flask(__name__)

    @app.route("/x")
    def view():
        return {}

    loader._register_openapi(app, "demo")
    assert FlaskMountRegistry.get("demo") == {
        "paths": {},
        "components": {},
        "mount_prefix": "/demo",
    }


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_try_self_spec_uses_app_schema():
    from flask import Flask

    app = Flask(__name__)

    class FakeApi:
        __schema__ = {
            "swagger": "2.0",
            "paths": {"/x": {"get": {}}},
            "definitions": {"M": {"type": "object"}},
        }

    app.extensions["restx"] = FakeApi()
    spec = FlaskIntrospector(app, "demo").try_self_spec()
    assert spec is not None
    assert "/x" in spec["paths"]
    assert spec["components"]["schemas"] == {"M": {"type": "object"}}


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_route_ids_root_falls_back_to_mount_name():
    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def home():
        """Home."""
        return {}

    routes, _ = FlaskIntrospector(app, "demo_flask").introspect()
    op = routes[0].operations[0]
    assert op.widget_id == "demo_flask"
    assert op.widget_name == "Demo Flask"


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_param_description_overlaid_from_docstring():
    from flask import Flask, request

    app = Flask(__name__)

    @app.route("/s")
    def search():
        """Search.

        Args:
            q: The query string.
        """
        return {"q": request.args.get("q")}

    routes, _ = FlaskIntrospector(app, "demo").introspect()
    params = {p.name: p for p in routes[0].operations[0].parameters}
    assert params["q"].description == "The query string."


def _v_str_annotation() -> str:
    return "x"


def test_returns_html_str_annotation():
    assert aa.returns_html(_v_str_annotation) is True


def test_returns_html_unreadable_is_false():
    assert aa.returns_html(len) is False


def _v_tuple_html():
    return ("<html>", 200)


def test_returns_html_tuple():
    assert aa.returns_html(_v_tuple_html) is True


def _v_make_response_html():
    from flask import make_response

    return make_response("<html>")


def test_returns_html_make_response():
    assert aa.returns_html(_v_make_response_html) is True


def _v_fstring_html():
    symbol = "AAPL"
    return f"<html><body>{symbol}</body></html>"


def test_returns_html_fstring():
    assert aa.returns_html(_v_fstring_html) is True


def _v_args_dynamic_subscript():
    from flask import request

    i = "k"
    return request.args[i]


def test_ast_args_dynamic_subscript_is_partial():
    _, _, _, partial = aa.analyze_view_source(_v_args_dynamic_subscript)
    assert partial is True


def _v_data_accessor():
    from flask import request

    return request.data.decode()


def test_ast_data_accessor_marks_binary_body():
    _, _, body, _ = aa.analyze_view_source(_v_data_accessor)
    assert body is not None
    assert body.media_type == "application/octet-stream"


def test_parse_google_skips_blank_and_stops_at_section():
    _, _, params = parse_docstring("S.\n\nArgs:\n\n    x: the x.\n\nReturns:\n    y\n")
    assert params == {"x": "the x."}


def test_parse_numpy_skips_blank_and_stops_at_section():
    _, _, params = parse_docstring(
        "S.\n\nParameters\n----------\nx\n    the x.\n\nReturns\n-------\n"
    )
    assert params == {"x": "the x."}


def test_dedup_suffixes_collisions():
    intro = FlaskIntrospector.__new__(FlaskIntrospector)
    intro._seen_ids = set()
    assert intro._dedup("a") == "a"
    assert intro._dedup("a") == "a_2"
    assert intro._dedup("a") == "a_3"


def test_model_ref_hoists_nested_defs():
    from pydantic import BaseModel

    from openbb_core.app.utils.flask.introspector import _model_ref

    class Inner(BaseModel):
        a: int

    class Outer(BaseModel):
        inner: Inner

    components: dict = {}
    ref = _model_ref(Outer, components)
    assert ref == {"$ref": "#/components/schemas/Outer"}
    assert "Inner" in components
    assert "Outer" in components


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_try_self_spec_handles_errors():
    from flask import Flask

    app = Flask(__name__)

    class BadApi:
        @property
        def __schema__(self):
            raise RuntimeError("nope")

    app.extensions["bad"] = BadApi()
    assert FlaskIntrospector(app, "demo").try_self_spec() is None


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_introspect_skips_routes_without_a_view():
    from flask import Flask

    app = Flask(__name__)

    @app.route("/x")
    def view():
        return {}

    intro = FlaskIntrospector(app, "demo")
    intro._view_functions = {}
    routes, _ = intro.introspect()
    assert routes == []


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
def test_operations_skips_class_method_not_implemented():
    from flask import Flask
    from flask.views import MethodView

    app = Flask(__name__)

    class Weird(MethodView):
        methods = ["GET", "DELETE"]

        def get(self):
            return {}

    app.add_url_rule("/w", view_func=Weird.as_view("w"))

    routes, _ = FlaskIntrospector(app, "demo").introspect()
    methods = {op.method for route in routes for op in route.operations}
    assert "get" in methods
    assert "delete" not in methods
