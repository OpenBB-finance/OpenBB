"""Static AST analysis of Flask view functions for parameters and body shape."""

from __future__ import annotations

import ast
import textwrap
from inspect import getsource
from typing import Any

from .types import BodyInfo, ParamInfo

_TYPE_MAP = {"int": "integer", "float": "number", "bool": "boolean", "str": "string"}
_QUERY_ATTRS = {"args", "values"}


def analyze_view_source(
    func: Any,
) -> tuple[list[ParamInfo], list[ParamInfo], BodyInfo | None, bool]:
    """Return ``(query_params, header_params, request_body, partial)`` for a view."""
    try:
        source = textwrap.dedent(getsource(func))
    except (OSError, TypeError):
        return [], [], None, True
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], [], None, True
    visitor = _RequestVisitor()
    visitor.visit(tree)
    return visitor.build()


def _is_request(node: ast.AST) -> bool:
    """Return ``True`` when ``node`` references the Flask ``request`` proxy."""
    return (isinstance(node, ast.Name) and node.id == "request") or (
        isinstance(node, ast.Attribute) and node.attr == "request"
    )


def _request_attr(node: ast.AST) -> str | None:
    """Return ``attr`` when ``node`` is ``request.<attr>``, else ``None``."""
    if isinstance(node, ast.Attribute) and _is_request(node.value):
        return node.attr
    return None


def _const_str(node: ast.AST | None) -> str | None:
    """Return the string value when ``node`` is a string constant."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _schema_for_type(name: str | None) -> dict[str, Any]:
    """Map a Python type name to an OpenAPI schema object."""
    return {"type": _TYPE_MAP.get(name or "", "string")}


def _object_schema(properties: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return an object schema, including ``properties`` when non-empty."""
    schema: dict[str, Any] = {"type": "object"}
    if properties:
        schema["properties"] = properties
    return schema


def returns_html(func: Any) -> bool:
    """Return ``True`` when a view appears to produce an HTML response."""
    annotation = getattr(func, "__annotations__", {}).get("return")
    if annotation is str or annotation == "str":
        return True
    try:
        tree = ast.parse(textwrap.dedent(getsource(func)))
    except (OSError, TypeError, SyntaxError):
        return False
    return any(
        isinstance(node, ast.Return) and _is_html_return(node.value)
        for node in ast.walk(tree)
    )


def _is_html_return(value: ast.AST | None) -> bool:
    """Return ``True`` when a return value is an HTML string or template render."""
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return True
    if isinstance(value, ast.JoinedStr):
        return True
    if isinstance(value, ast.Tuple) and value.elts:
        return _is_html_return(value.elts[0])
    if isinstance(value, ast.Call):
        func = value.func
        name = (
            func.attr
            if isinstance(func, ast.Attribute)
            else func.id
            if isinstance(func, ast.Name)
            else ""
        )
        if name in {"render_template", "render_template_string"}:
            return True
        if name in {"make_response", "Response"} and value.args:
            return _is_html_return(value.args[0])
    return False


class _RequestVisitor(ast.NodeVisitor):
    """Collect request parameters and body shape from a view function body."""

    def __init__(self) -> None:
        """Initialise empty collectors."""
        self._query: dict[str, ParamInfo] = {}
        self._headers: dict[str, ParamInfo] = {}
        self._form: dict[str, dict[str, Any]] = {}
        self._json: dict[str, dict[str, Any]] = {}
        self._bindings: dict[str, str] = {}
        self._body_kinds: set[str] = set()
        self.partial = False

    def visit_Assign(self, node: ast.Assign) -> None:
        """Track ``var = request.<source>`` bindings and body presence."""
        kind = self._assign_kind(node.value)
        if kind:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._bindings[target.id] = kind
            self._mark_body(kind)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Handle ``<source>.get/getlist/to_dict`` accessors."""
        func = node.func
        if isinstance(func, ast.Attribute):
            if _request_attr(func) == "get_json":
                self._mark_body("json")
            else:
                self._handle_accessor(func.attr, func.value, node)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Handle ``<source>["key"]`` access."""
        kind = self._base_kind(node.value)
        key = _const_str(node.slice)
        if kind and key:
            self._record(kind, key, _schema_for_type("str"), required=True)
        elif kind:
            self.partial = True
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Mark a request body present from a bare ``request.<body>`` access."""
        attr = _request_attr(node)
        if attr in {"json", "form", "files", "data"}:
            self._mark_body("binary" if attr == "data" else attr)
        self.generic_visit(node)

    def _assign_kind(self, value: ast.AST) -> str | None:
        """Classify the right-hand side of an assignment as a request source."""
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and _request_attr(value.func) == "get_json"
        ):
            return "json"
        return self._base_kind(value)

    def _base_kind(self, node: ast.AST) -> str | None:
        """Resolve a node to a request source kind, following local bindings."""
        attr = _request_attr(node)
        if attr in _QUERY_ATTRS:
            return "args"
        if attr in {"form", "files", "headers", "json"}:
            return attr
        if attr == "data":
            return "binary"
        if isinstance(node, ast.Name):
            return self._bindings.get(node.id)
        return None

    def _handle_accessor(self, method: str, base: ast.AST, node: ast.Call) -> None:
        """Record a parameter discovered through ``.get``/``.getlist``."""
        kind = self._base_kind(base)
        if not kind:
            return
        if method == "to_dict":
            self.partial = True
            return
        if method not in {"get", "getlist"}:
            return
        key = _const_str(node.args[0]) if node.args else None
        if key is None:
            self.partial = True
            return
        type_name = self._keyword_type(node)
        schema = _schema_for_type(type_name)
        if method == "getlist":
            schema = {"type": "array", "items": schema}
        example = self._default_example(node)
        self._record(kind, key, schema, required=False, example=example)

    @staticmethod
    def _keyword_type(node: ast.Call) -> str | None:
        """Return the ``type=`` keyword's type name, if a simple builtin."""
        for keyword in node.keywords:
            if keyword.arg == "type" and isinstance(keyword.value, ast.Name):
                return keyword.value.id
        return None

    @staticmethod
    def _default_example(node: ast.Call) -> Any | None:
        """Return the default value if it is a constant."""
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
            return node.args[1].value
        for keyword in node.keywords:
            if keyword.arg == "default" and isinstance(keyword.value, ast.Constant):
                return keyword.value.value
        return None

    def _record(
        self,
        kind: str,
        key: str,
        schema: dict[str, Any],
        *,
        required: bool,
        example: Any | None = None,
    ) -> None:
        """Store a discovered parameter or body property by source kind."""
        if kind == "args":
            self._query[key] = ParamInfo(
                key, "query", schema, required=required, example=example
            )
        elif kind == "headers":
            self._headers[key] = ParamInfo(key, "header", schema, required=required)
        elif kind == "form":
            self._mark_body("form")
            self._form[key] = schema
        elif kind == "files":
            self._mark_body("files")
            self._form[key] = {"type": "string", "format": "binary"}
        elif kind == "json":
            self._mark_body("json")
            self._json[key] = schema

    def _mark_body(self, kind: str) -> None:
        """Note that the view consumes a request body of ``kind``."""
        self._body_kinds.add(kind)

    def build(
        self,
    ) -> tuple[list[ParamInfo], list[ParamInfo], BodyInfo | None, bool]:
        """Return the collected query params, header params, body and partial flag."""
        return (
            list(self._query.values()),
            list(self._headers.values()),
            self._build_body(),
            self.partial,
        )

    def _build_body(self) -> BodyInfo | None:
        """Synthesise a request body from the discovered body usage."""
        kinds = self._body_kinds
        if "json" in kinds:
            return BodyInfo(
                "application/json",
                _object_schema(self._json),
                required=bool(self._json),
            )
        if "files" in kinds:
            return BodyInfo(
                "multipart/form-data",
                _object_schema(self._form),
                required=bool(self._form),
            )
        if "form" in kinds:
            return BodyInfo(
                "application/x-www-form-urlencoded",
                _object_schema(self._form),
                required=bool(self._form),
            )
        if "binary" in kinds:
            return BodyInfo(
                "application/octet-stream", {"type": "string", "format": "binary"}
            )
        return None
