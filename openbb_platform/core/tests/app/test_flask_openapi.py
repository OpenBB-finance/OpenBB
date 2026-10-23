"""Tests for Flask OpenAPI generation, the mount registry and live mounting."""

import importlib.util
from unittest.mock import PropertyMock, patch

import pytest

from openbb_core.app.utils.flask.openapi import OpenAPISpecGenerator
from openbb_core.app.utils.flask.registry import FlaskMountRegistry
from openbb_core.app.utils.flask.types import OperationInfo, ParamInfo, RouteInfo

FLASK_AVAILABLE = importlib.util.find_spec("flask") is not None


@pytest.fixture(autouse=True)
def _reset_registry():
    """Reset the registry around each test so global state never leaks."""
    FlaskMountRegistry.reset()
    yield
    FlaskMountRegistry.reset()


def test_openapi_generator_builds_operation():
    route = RouteInfo(
        path="/items/{item_id}",
        operations=[
            OperationInfo(
                method="get",
                operation_id="get_item",
                summary="Get item",
                parameters=[
                    ParamInfo("item_id", "path", {"type": "integer"}, required=True),
                    ParamInfo("verbose", "query", {"type": "boolean"}),
                ],
            )
        ],
    )
    spec = OpenAPISpecGenerator([route]).generate()
    operation = spec["paths"]["/items/{item_id}"]["get"]

    assert operation["operationId"] == "get_item"
    assert operation["summary"] == "Get item"
    params = {p["name"]: p for p in operation["parameters"]}
    assert params["item_id"]["in"] == "path"
    assert params["item_id"]["required"] is True
    assert params["verbose"]["in"] == "query"
    assert "application/json" in operation["responses"]["200"]["content"]


def test_openapi_generator_lifts_auth_header_to_security():
    route = RouteInfo(
        path="/secure",
        operations=[
            OperationInfo(
                method="get",
                operation_id="secure",
                parameters=[ParamInfo("Authorization", "header", {"type": "string"})],
            )
        ],
    )
    spec = OpenAPISpecGenerator([route]).generate()
    operation = spec["paths"]["/secure"]["get"]

    assert {"bearerAuth": []} in operation["security"]
    assert "bearerAuth" in spec["components"]["securitySchemes"]
    assert all(p["name"] != "Authorization" for p in operation.get("parameters", []))


def test_openapi_generator_serialises_request_body():
    from openbb_core.app.utils.flask.types import BodyInfo

    route = RouteInfo(
        path="/items",
        operations=[
            OperationInfo(
                method="post",
                operation_id="create_item",
                request_body=BodyInfo(
                    "application/json",
                    {"type": "object", "properties": {"name": {"type": "string"}}},
                    required=True,
                ),
            )
        ],
    )
    spec = OpenAPISpecGenerator([route]).generate()
    body = spec["paths"]["/items"]["post"]["requestBody"]
    assert body["required"] is True
    assert "application/json" in body["content"]


def test_openapi_generator_emits_widget_and_mcp_config():
    route = RouteInfo(
        path="/w",
        operations=[
            OperationInfo(
                method="get",
                operation_id="w",
                widget_config={"name": "W", "type": "table"},
                mcp_config={"enabled": True},
            )
        ],
    )
    operation = OpenAPISpecGenerator([route]).generate()["paths"]["/w"]["get"]
    assert operation["widget_config"] == {"name": "W", "type": "table"}
    assert operation["mcp_config"] == {"enabled": True}


def test_widget_config_ids_exclude_path_params():
    route = RouteInfo(
        path="/quote/{symbol}",
        operations=[
            OperationInfo(
                method="get",
                operation_id="demo_flask_quote",
                widget_id="demo_flask_quote",
                widget_name="Quote",
            )
        ],
    )
    config = OpenAPISpecGenerator([route]).generate()["paths"]["/quote/{symbol}"][
        "get"
    ]["widget_config"]
    assert config["widgetId"] == "demo_flask_quote"
    assert config["mcp_tool"]["tool_id"] == "demo_flask_quote"
    assert config["name"] == "Quote"


def test_widget_config_author_values_win():
    route = RouteInfo(
        path="/quote/{symbol}",
        operations=[
            OperationInfo(
                method="get",
                operation_id="demo_flask_quote",
                widget_id="demo_flask_quote",
                widget_name="Quote",
                widget_config={"name": "Latest Quote", "type": "table"},
            )
        ],
    )
    config = OpenAPISpecGenerator([route]).generate()["paths"]["/quote/{symbol}"][
        "get"
    ]["widget_config"]
    assert config["name"] == "Latest Quote"
    assert config["widgetId"] == "demo_flask_quote"
    assert config["type"] == "table"


def test_widget_config_html_response_sets_type_html():
    route = RouteInfo(
        path="/page",
        operations=[
            OperationInfo(
                method="get",
                operation_id="demo_page",
                widget_id="demo_page",
                widget_name="Page",
                responses={
                    "200": {"content": {"text/html": {"schema": {"type": "string"}}}}
                },
            )
        ],
    )
    config = OpenAPISpecGenerator([route]).generate()["paths"]["/page"]["get"][
        "widget_config"
    ]
    assert config["type"] == "html"


def test_registry_aggregate_applies_global_and_mount_prefix():
    FlaskMountRegistry.register(
        "demo", {"/data": {"get": {"operationId": "data"}}}, {"schemas": {}}
    )
    merged = FlaskMountRegistry.aggregate("/api/v1")
    assert "/api/v1/demo/data" in merged["paths"]


def test_registry_reset_prevents_state_leak():
    FlaskMountRegistry.register("a", {"/x": {}}, {})
    assert "a" in FlaskMountRegistry.names()
    FlaskMountRegistry.reset()
    assert FlaskMountRegistry.names() == []


def test_registry_register_is_idempotent_by_name():
    FlaskMountRegistry.register("demo", {"/v1": {}}, {})
    FlaskMountRegistry.register("demo", {"/v2": {}}, {})
    merged = FlaskMountRegistry.aggregate("")
    assert "/demo/v2" in merged["paths"]
    assert "/demo/v1" not in merged["paths"]


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
@patch(
    "openbb_core.app.extension_loader.ExtensionLoader.flask_objects",
    new_callable=PropertyMock,
)
def test_mount_flask_extensions_mounts_and_registers(mock_flask_objects):
    from fastapi import FastAPI
    from flask import Flask
    from starlette.routing import Mount

    from openbb_core.app.utils.flask import mount_flask_extensions

    flask_app = Flask(__name__)

    @flask_app.route("/data")
    def data():
        """Get data."""
        return {"ok": True}

    mock_flask_objects.return_value = {"demo": flask_app}

    api = FastAPI()
    mount_flask_extensions(api, "/api/v1")

    mount_paths = [r.path for r in api.routes if isinstance(r, Mount)]
    assert "/api/v1/demo" in mount_paths
    assert "demo" in FlaskMountRegistry.names()


@patch(
    "openbb_core.app.extension_loader.ExtensionLoader.flask_objects",
    new_callable=PropertyMock,
)
def test_mount_flask_extensions_without_a2wsgi_skips_mount(
    mock_flask_objects, monkeypatch, caplog
):
    import builtins

    from fastapi import FastAPI

    from openbb_core.app.utils.flask import mount_flask_extensions

    real_import = builtins.__import__

    def _no_a2wsgi(name, *args, **kwargs):
        if name == "a2wsgi":
            raise ImportError("No module named 'a2wsgi'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _no_a2wsgi)
    mock_flask_objects.return_value = {"demo": object()}

    api = FastAPI()
    routes_before = list(api.routes)
    with caplog.at_level("WARNING", logger="openbb_core.app.utils.flask"):
        mount_flask_extensions(api, "/api/v1")

    assert api.routes == routes_before
    assert FlaskMountRegistry.names() == []
    assert "openbb-core[flask]" in caplog.text


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask is not installed")
@patch(
    "openbb_core.app.extension_loader.ExtensionLoader.flask_objects",
    new_callable=PropertyMock,
)
def test_wsgi_mount_serves_flask_and_documents_routes(mock_flask_objects):
    from fastapi import FastAPI
    from flask import Flask
    from starlette.testclient import TestClient

    from openbb_core.app.utils.flask import (
        merge_flask_openapi,
        mount_flask_extensions,
    )

    flask_app = Flask(__name__)
    hits: dict[str, bool] = {}

    @flask_app.before_request
    def _before():
        hits["before"] = True

    @flask_app.route("/hello")
    def hello():
        """Say hello."""
        return {"msg": "hi"}

    mock_flask_objects.return_value = {"demo": flask_app}

    api = FastAPI()
    mount_flask_extensions(api, "/api/v1")

    response = TestClient(api).get("/api/v1/demo/hello")

    assert response.status_code == 200
    assert response.json() == {"msg": "hi"}
    assert hits.get("before") is True

    schema = merge_flask_openapi({"paths": {}, "components": {}}, "/api/v1")
    assert "/api/v1/demo/hello" in schema["paths"]


def test_mount_flask_extensions_with_no_flask_apps():
    """Test mount_flask_extensions when there are no Flask apps."""
    from unittest.mock import PropertyMock, patch

    from fastapi import FastAPI

    from openbb_core.app.utils.flask import mount_flask_extensions

    with patch(
        "openbb_core.app.extension_loader.ExtensionLoader.flask_objects",
        new_callable=PropertyMock,
        return_value={},
    ):
        api = FastAPI()
        routes_before = list(api.routes)
        mount_flask_extensions(api)
        assert api.routes == routes_before


def test_merge_flask_openapi_with_no_registered_apps():
    """Test merge_flask_openapi when no Flask apps are registered."""
    from openbb_core.app.utils.flask import merge_flask_openapi

    schema = {"paths": {}, "components": {}}
    result = merge_flask_openapi(schema)
    assert result == {"paths": {}, "components": {}}


def test_merge_flask_openapi_with_existing_paths():
    """Test merge_flask_openapi merges into existing paths."""
    from openbb_core.app.utils.flask import merge_flask_openapi

    FlaskMountRegistry.register("ext", {"/new": {"get": {}}}, {"schemas": {"Obj": {}}})
    schema = {
        "paths": {"/old": {"get": {}}},
        "components": {"schemas": {"OldObj": {}}},
    }
    result = merge_flask_openapi(schema, "/api")
    assert "/api/ext/new" in result["paths"]
    assert "/old" in result["paths"]
    assert "Obj" in result["components"]["schemas"]
    assert "OldObj" in result["components"]["schemas"]
