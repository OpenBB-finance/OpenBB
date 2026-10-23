"""Introspect a Flask application into framework-neutral ``RouteInfo`` objects."""

from __future__ import annotations

import logging
import re
from typing import Any

from pydantic import BaseModel

from .ast_analysis import analyze_view_source, returns_html
from .docstrings import parse_docstring
from .types import OperationInfo, ParamInfo, RouteInfo

logger = logging.getLogger("openbb_core.app.utils.flask")

_CONVERTER_SCHEMA = {
    "IntegerConverter": {"type": "integer"},
    "FloatConverter": {"type": "number"},
    "UUIDConverter": {"type": "string", "format": "uuid"},
    "PathConverter": {"type": "string"},
    "UnicodeConverter": {"type": "string"},
}
_PATH_ARG = re.compile(r"<(?:[^:<>]+:)?([^<>]+)>")
_PARAM_SEG = re.compile(r"<[^>]+>")
_SKIP_METHODS = {"HEAD", "OPTIONS"}


class FlaskIntrospector:
    """Extract OpenAPI metadata from a Flask application's URL map."""

    def __init__(self, flask_app: Any, name: str = "") -> None:
        """Store the Flask app, its URL map, view registry and mount name."""
        self._app = flask_app
        self._name = name.strip("/")
        self._url_map = flask_app.url_map
        self._view_functions = flask_app.view_functions
        self._seen_ids: set[str] = set()

    def introspect(self) -> tuple[list[RouteInfo], dict[str, Any]]:
        """Return ``(routes, component_schemas)`` for the application."""
        routes: list[RouteInfo] = []
        components: dict[str, Any] = {}
        for rule in self._url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            operations = self._operations(rule, components)
            if operations:
                routes.append(
                    RouteInfo(path=self._openapi_path(rule.rule), operations=operations)
                )
        return routes, components

    def try_self_spec(self) -> dict[str, Any] | None:
        """Return the app's own OpenAPI spec if one is available."""
        try:
            with self._app.app_context():
                for ext in getattr(self._app, "extensions", {}).values():
                    api = getattr(ext, "api", ext)
                    schema = getattr(api, "__schema__", None)
                    if isinstance(schema, dict) and schema.get("paths"):
                        return _swagger2_to_openapi3(schema)
        except Exception as exc:
            logger.debug("Flask self-spec detection failed: %s", exc)
        return None

    def _operations(self, rule: Any, components: dict[str, Any]) -> list[OperationInfo]:
        """Build the operations for a single URL rule."""
        methods = sorted(set(rule.methods) - _SKIP_METHODS)
        path_params = self._path_params(rule)
        view = self._view_functions.get(rule.endpoint)
        if view is None:
            return []
        view_class = getattr(view, "view_class", None)
        multi_method = len(methods) > 1
        operations: list[OperationInfo] = []
        for method in methods:
            func = getattr(view_class, method.lower(), None) if view_class else view
            if func is None:
                continue
            operations.append(
                self._build_operation(
                    func, method, rule, path_params, components, multi_method
                )
            )
        return operations

    def _build_operation(
        self,
        func: Any,
        method: str,
        rule: Any,
        path_params: list[ParamInfo],
        components: dict[str, Any],
        multi_method: bool,
    ) -> OperationInfo:
        """Assemble one OpenAPI operation from a view callable."""
        summary, description, param_docs = parse_docstring(
            getattr(func, "__doc__", None)
        )
        query, headers, body, partial = analyze_view_source(func)
        parameters = [*path_params, *query, *headers]
        for param in parameters:
            if not param.description and param.name in param_docs:
                param.description = param_docs[param.name]
        route_id, widget_name = self._route_ids(rule)
        operation_id = f"{route_id}_{method.lower()}" if multi_method else route_id
        return OperationInfo(
            method=method.lower(),
            operation_id=self._dedup(operation_id),
            summary=summary,
            description=description,
            parameters=parameters,
            request_body=body,
            responses=self._responses(func, components),
            partial=partial,
            widget_id=route_id,
            widget_name=widget_name,
            widget_config=getattr(func, "widget_config", None),
            mcp_config=getattr(func, "mcp_config", None),
        )

    def _route_ids(self, rule: Any) -> tuple[str, str]:
        """Return a clean ``(route_id, display_name)`` from the rule, sans params."""
        tail = [seg for seg in _PARAM_SEG.sub("", rule.rule).split("/") if seg]
        segments = [self._name, *tail] if self._name else tail
        route_id = "_".join(dict.fromkeys(seg for seg in segments if seg))
        name = " ".join(tail).replace("_", " ").title()
        return route_id, name or self._name.replace("_", " ").title()

    def _path_params(self, rule: Any) -> list[ParamInfo]:
        """Build path parameters from the rule's Werkzeug converters."""
        params: list[ParamInfo] = []
        converters = getattr(rule, "_converters", {})
        for arg in rule.arguments:
            converter = converters.get(arg)
            schema = self._converter_schema(converter, rule.rule, arg)
            params.append(ParamInfo(arg, "path", schema, required=True))
        return params

    @staticmethod
    def _converter_schema(converter: Any, rule_str: str, arg: str) -> dict[str, Any]:
        """Map a Werkzeug converter to an OpenAPI schema."""
        if converter is None:
            return {"type": "string"}
        name = type(converter).__name__
        if name == "AnyConverter":
            return {"type": "string", "enum": _any_enum(rule_str, arg)}
        return dict(_CONVERTER_SCHEMA.get(name, {"type": "string"}))

    @staticmethod
    def _responses(func: Any, components: dict[str, Any]) -> dict[str, Any]:
        """Build a best-effort 200 response from the return annotation or source."""
        annotation = getattr(func, "__annotations__", {}).get("return")
        content: dict[str, Any]
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            content = {
                "application/json": {"schema": _model_ref(annotation, components)}
            }
        elif returns_html(func):
            content = {"text/html": {"schema": {"type": "string"}}}
        else:
            content = {"application/json": {"schema": {"type": "object"}}}
        return {
            "200": {
                "description": "Successful Response",
                "content": content,
            }
        }

    def _dedup(self, operation_id: str) -> str:
        """Return a unique operationId, suffixing collisions."""
        candidate = operation_id
        suffix = 2
        while candidate in self._seen_ids:
            candidate = f"{operation_id}_{suffix}"
            suffix += 1
        self._seen_ids.add(candidate)
        return candidate

    @staticmethod
    def _openapi_path(rule: str) -> str:
        """Convert a Werkzeug rule to an OpenAPI path."""
        return _PATH_ARG.sub(r"{\1}", rule)


def _any_enum(rule_str: str, arg: str) -> list[str]:
    """Parse the ordered choices of ``<any(...):arg>`` from the rule source."""
    match = re.search(rf"<any\(([^)]*)\):{re.escape(arg)}>", rule_str)
    if not match:
        return []
    return [choice.strip().strip("'\"") for choice in match.group(1).split(",")]


def _model_ref(model: type[BaseModel], components: dict[str, Any]) -> dict[str, Any]:
    """Add a Pydantic model schema to ``components`` and return a ``$ref``."""
    schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
    for name, definition in schema.pop("$defs", {}).items():
        components.setdefault(name, definition)
    components[model.__name__] = schema
    return {"$ref": f"#/components/schemas/{model.__name__}"}


def _swagger2_to_openapi3(schema: dict[str, Any]) -> dict[str, Any]:
    """Normalise a Swagger 2.0 schema to OpenAPI 3 paths and components."""
    if str(schema.get("openapi", "")).startswith("3"):
        return {
            "paths": schema.get("paths", {}),
            "components": schema.get("components", {}),
        }
    components: dict[str, Any] = {"schemas": schema.get("definitions", {})}
    return {"paths": schema.get("paths", {}), "components": components}
