"""Typed data structures describing introspected Flask routes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ParamInfo:
    """A single OpenAPI parameter."""

    name: str
    location: str
    schema: dict[str, Any]
    required: bool = False
    description: str | None = None
    example: Any | None = None


@dataclass(slots=True)
class BodyInfo:
    """An OpenAPI request body."""

    media_type: str
    schema: dict[str, Any]
    required: bool = False


@dataclass(slots=True)
class OperationInfo:
    """A single HTTP operation bound to a Flask route."""

    method: str
    operation_id: str
    summary: str | None = None
    description: str | None = None
    parameters: list[ParamInfo] = field(default_factory=list)
    request_body: BodyInfo | None = None
    responses: dict[str, Any] = field(default_factory=dict)
    security: list[dict[str, list[str]]] | None = None
    partial: bool = False
    widget_id: str = ""
    widget_name: str | None = None
    widget_config: dict[str, Any] | None = None
    mcp_config: dict[str, Any] | None = None


@dataclass(slots=True)
class RouteInfo:
    """A Flask URL rule and the operations it exposes."""

    path: str
    operations: list[OperationInfo] = field(default_factory=list)
