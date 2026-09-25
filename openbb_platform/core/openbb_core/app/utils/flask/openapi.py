"""Convert introspected Flask routes into an OpenAPI 3 fragment."""

from __future__ import annotations

from typing import Any

from .types import OperationInfo, ParamInfo, RouteInfo

_AUTH_HEADER = "authorization"
_API_KEY_HEADER = "x-api-key"
_DEFAULT_RESPONSES = {
    "200": {
        "description": "Successful Response",
        "content": {"application/json": {"schema": {"type": "object"}}},
    }
}


class OpenAPISpecGenerator:
    """Build an OpenAPI ``{"paths", "components"}`` fragment from routes."""

    def __init__(
        self, routes: list[RouteInfo], components: dict[str, Any] | None = None
    ) -> None:
        """Store the routes and any pre-collected component schemas."""
        self._routes = routes
        self._schemas = dict(components or {})
        self._security_schemes: dict[str, Any] = {}

    def generate(self) -> dict[str, Any]:
        """Return the OpenAPI fragment for all routes."""
        paths: dict[str, Any] = {}
        for route in self._routes:
            item = paths.setdefault(route.path, {})
            for operation in route.operations:
                item[operation.method] = self._operation(operation)

        components: dict[str, Any] = {}
        if self._schemas:
            components["schemas"] = self._schemas
        if self._security_schemes:
            components["securitySchemes"] = self._security_schemes
        return {"paths": paths, "components": components}

    def _operation(self, operation: OperationInfo) -> dict[str, Any]:
        """Serialise a single operation object."""
        params, security = self._split_security(operation.parameters)
        result: dict[str, Any] = {
            "operationId": operation.operation_id,
            "tags": ["flask"],
            "responses": operation.responses or _DEFAULT_RESPONSES,
        }
        if operation.summary:
            result["summary"] = operation.summary
        if operation.description:
            result["description"] = operation.description
        if params:
            result["parameters"] = [_param_to_openapi(param) for param in params]
        if operation.request_body:
            body = operation.request_body
            result["requestBody"] = {
                "required": body.required,
                "content": {body.media_type: {"schema": body.schema}},
            }
        if security:
            result["security"] = security
        widget_config = self._widget_config(operation)
        if widget_config:
            result["widget_config"] = widget_config
        if operation.mcp_config is not None:
            result["mcp_config"] = operation.mcp_config
        if operation.partial:
            result["x-openbb-introspection"] = "partial"
        return result

    @staticmethod
    def _widget_config(operation: OperationInfo) -> dict[str, Any]:
        """Build widget_config with clean identifiers, letting author values win."""
        config: dict[str, Any] = dict(operation.widget_config or {})
        if operation.widget_id:
            config.setdefault("widgetId", operation.widget_id)
            if operation.widget_name:
                config.setdefault("name", operation.widget_name)
            mcp_tool = config.setdefault("mcp_tool", {})
            if isinstance(mcp_tool, dict):
                mcp_tool.setdefault("tool_id", operation.widget_id)
        content = operation.responses.get("200", {}).get("content", {})
        if "text/html" in content:
            config.setdefault("type", "html")
        return config

    def _split_security(
        self, params: list[ParamInfo]
    ) -> tuple[list[ParamInfo], list[dict[str, list[str]]]]:
        """Lift recognised auth headers into security schemes."""
        kept: list[ParamInfo] = []
        security: list[dict[str, list[str]]] = []
        for param in params:
            name = param.name.lower()
            if param.location == "header" and name == _AUTH_HEADER:
                self._security_schemes["bearerAuth"] = {
                    "type": "http",
                    "scheme": "bearer",
                }
                security.append({"bearerAuth": []})
            elif param.location == "header" and name == _API_KEY_HEADER:
                self._security_schemes["apiKeyAuth"] = {
                    "type": "apiKey",
                    "in": "header",
                    "name": param.name,
                }
                security.append({"apiKeyAuth": []})
            else:
                kept.append(param)
        return kept, security


def _param_to_openapi(param: ParamInfo) -> dict[str, Any]:
    """Serialise a ``ParamInfo`` into an OpenAPI parameter object."""
    out: dict[str, Any] = {
        "name": param.name,
        "in": param.location,
        "required": param.required,
        "schema": param.schema,
    }
    if param.description:
        out["description"] = param.description
    if param.example is not None:
        out["example"] = param.example
    return out
