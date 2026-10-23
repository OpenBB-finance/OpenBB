"""Utilities for handling FastAPI routes."""

import inspect
import re
import sys
from collections.abc import Sequence
from types import UnionType
from typing import Any, Union, cast, get_args, get_origin

from fastapi import FastAPI
from fastapi.routing import APIRoute, iter_route_contexts
from fastmcp.server.providers.openapi import MCPType, RouteMap
from fastmcp.utilities.openapi import HttpMethod
from openbb_core.app.service.system_service import SystemService
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from openbb_mcp_server.models.mcp_config import MCPConfigModel, validate_mcp_config
from openbb_mcp_server.models.settings import MCPSettings


class ProcessedRouteData:
    """Container for all data collected during route processing."""

    def __init__(self):
        """Initialize with empty lists and dictionaries."""
        self.route_maps: list[RouteMap] = []
        self.route_lookup: dict[tuple[str, str], APIRoute] = {}
        self.excluded_routes: list[APIRoute] = []
        self.prompt_definitions: list[dict] = []
        self.exposed_methods: dict[str, set[str]] = {}


def get_api_prefix(settings: MCPSettings | None) -> str:
    """Get normalized API prefix (leading slash, no trailing slash)."""
    override = getattr(settings, "api_prefix", None)
    if isinstance(override, str) and override.strip():
        prefix = override
    else:
        prefix = SystemService().system_settings.api_settings.prefix or ""
    prefix = "/" + prefix.lstrip("/")
    if prefix.endswith("/"):
        prefix = prefix[:-1]
    return prefix


def strip_api_prefix(path: str, api_prefix: str) -> str:
    """Strip the exact API prefix from a path and return the remainder without a leading slash."""
    if not path:
        return ""
    if not path.startswith("/"):
        path = "/" + path
    remainder = (
        path[len(api_prefix) :] if api_prefix and path.startswith(api_prefix) else path
    )
    return remainder.lstrip("/")


def route_naming(path: str, api_prefix: str) -> tuple[str, str, str]:
    """Return the category, subcategory, and default tool name of a route path.

    Parameters
    ----------
    path : str
        The route path as served.
    api_prefix : str
        The normalized API prefix to strip first.

    Returns
    -------
    tuple[str, str, str]
        The category (first segment), the subcategory (second segment of paths with
        three or more segments, else ``general``), and the tool name built from them.
    """
    local_path = strip_api_prefix(path, api_prefix)
    segments = [seg for seg in local_path.split("/") if seg and "{" not in seg]
    if not segments:
        return "general", "general", "general_root"
    category = segments[0]
    if len(segments) <= 2:
        return category, "general", f"{category}_{segments[-1]}"
    subcategory = segments[1]
    return category, subcategory, f"{category}_{subcategory}_{'_'.join(segments[2:])}"


def tool_name_for_route(
    path: str,
    method: str,
    api_prefix: str,
    exposed_methods: dict[str, set[str]],
    override: str | None = None,
) -> str:
    """Return the MCP tool name of one method of a route.

    Parameters
    ----------
    path : str
        The route path as served.
    method : str
        The HTTP method, upper case.
    api_prefix : str
        The normalized API prefix.
    exposed_methods : dict[str, set[str]]
        The methods exposed at each path.
    override : str | None
        A name set in the route's ``mcp_config``, used as given.

    Returns
    -------
    str
        The tool name; non-GET methods of a path that exposes several methods get a
        ``_<method>`` suffix so every tool name is unique.
    """
    if override:
        return override
    name = route_naming(path, api_prefix)[2]
    if method != "GET" and len(exposed_methods.get(path, ())) > 1:
        return f"{name}_{method.lower()}"
    return name


def _get_module_exclusion_targets(settings: MCPSettings | None) -> dict[str, str]:
    """Map each excluded path segment to the module whose presence hides it; an empty mapping hides nothing."""
    override = getattr(settings, "module_exclusion_map", None)
    if isinstance(override, dict):
        return {str(k): str(v) for k, v in override.items()}
    return {"coverage": "openbb_core"}


def get_mcp_config(route: APIRoute, *, strict: bool = False) -> MCPConfigModel:
    """Read and validate per-route MCP config from openapi_extra."""
    extra = route.openapi_extra or {}
    raw_config = extra.get("mcp_config") or extra.get("x-mcp") or {}

    if not isinstance(raw_config, dict):
        if strict:
            raise TypeError("mcp_config must be a dictionary.")
        raw_config = {}

    return validate_mcp_config(raw_config, strict=strict)


def _get_prompt_configs(route: APIRoute) -> list[dict]:
    """Extract prompt configurations from per-route MCP config."""
    mcp_cfg = get_mcp_config(route)
    return [p.model_dump(exclude_none=True) for p in mcp_cfg.prompts]


def _type_name(annotation: Any) -> str:
    """Return the class name of a parameter annotation, unwrapping ``X | None``, or ``str`` for anything else."""
    members = (
        [arg for arg in get_args(annotation) if arg is not type(None)]
        if get_origin(annotation) in (Union, UnionType)
        else [annotation]
    )
    if (
        len(members) == 1
        and isinstance(members[0], type)
        and get_origin(members[0]) is None
        and members[0] is not inspect.Parameter.empty
    ):
        return members[0].__name__
    return "str"


def _endpoint_argument(parameter: inspect.Parameter) -> dict:
    """Return the prompt argument definition of an endpoint parameter, with a default only when the parameter has one."""
    argument = {"name": parameter.name, "type": _type_name(parameter.annotation)}
    default = parameter.default
    if isinstance(default, FieldInfo):
        default = default.default
    if not any(default is unset for unset in (parameter.empty, ..., PydanticUndefined)):
        argument["default"] = default
    return argument


def _create_prompt_definitions_for_route(
    route: APIRoute,
    settings: MCPSettings | None = None,
    path: str | None = None,
    tool_name: str | None = None,
) -> list[dict]:
    """Create prompt definitions for a route served at ``path`` (default ``route.path``) as the tool ``tool_name``."""
    prompt_configs = _get_prompt_configs(route)
    definitions: list[dict] = []

    if not prompt_configs:
        return definitions

    endpoint_args = {
        p.name: _endpoint_argument(p)
        for p in inspect.signature(route.endpoint).parameters.values()
        if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
    }

    route_path = path or route.path
    if not route_path.startswith("/"):
        route_path = "/" + route_path
    default_name = route_naming(route_path, get_api_prefix(settings))[2]
    tool_uri = tool_name or get_mcp_config(route).name or default_name

    for i, prompt_cfg in enumerate(prompt_configs):
        prompt_name = prompt_cfg.get("name")
        if not prompt_name:
            suffix = f"_{i}" if len(prompt_configs) > 1 else ""
            prompt_name = f"{default_name}_prompt{suffix}"

        final_args: dict = {}
        prompt_arg_defs = {arg["name"]: arg for arg in prompt_cfg.get("arguments", [])}
        content = (
            f"Use the tool, {tool_uri}, to perform the following task.\n\n"
            + prompt_cfg.get("content", "")
        )

        prompt_vars = re.findall(r"\{(\w+)\}", content)

        for var in dict.fromkeys(prompt_vars):
            if var in prompt_arg_defs:
                final_args[var] = prompt_arg_defs[var]
            elif var in endpoint_args:
                final_args[var] = endpoint_args[var]
            else:
                final_args[var] = {"name": var, "type": "str"}

        prompt_def = {
            "name": prompt_name,
            "description": prompt_cfg.get("description") or f"Prompt for {tool_uri}",
            "content": content,
            "arguments": list(final_args.values()),
            "tool": tool_uri,
        }

        tags = list(prompt_cfg.get("tags", []))
        if route_path not in tags:
            tags.insert(0, route_path)
        prompt_def["tags"] = tags

        definitions.append(prompt_def)

    return definitions


def _normalize_methods(methods: Sequence[str] | None) -> list[str]:
    """Uppercase and filter out HEAD/OPTIONS."""
    if not methods:
        return []
    out = []
    for m in methods:
        if not m:
            continue
        mu = str(m).upper()
        if mu in {"HEAD", "OPTIONS"}:
            continue
        out.append(mu)
    return out


def _methods_from_config_or_route(cfg: MCPConfigModel, route: APIRoute) -> list:
    """Pull methods from cfg.methods if present; otherwise from route.methods."""
    if cfg.methods:
        if any(m.value == "*" for m in cfg.methods):
            return ["*"]
        methods = [m.value for m in cfg.methods]
    else:
        methods = list(route.methods or [])
    return _normalize_methods(methods)


def _resolve_mcp_type(value: str | None) -> MCPType | None:
    if not value:
        return None
    v = value.lower().strip()
    if v == "tool":
        return MCPType.TOOL
    if v == "resource":
        return MCPType.RESOURCE
    if v in {"resource_template", "resource-template"}:
        return MCPType.RESOURCE_TEMPLATE
    return None


def _should_exclude_by_module_and_path(path: str, settings: MCPSettings | None) -> bool:
    """Exclude only specific route trees if the corresponding module is loaded."""
    api_prefix = get_api_prefix(settings)
    targets = _get_module_exclusion_targets(settings)

    if not path.startswith("/"):
        path = "/" + path

    for segment, module_name in targets.items():
        base = f"{api_prefix}/{segment}"
        if path.startswith(base) and module_name in sys.modules:
            return True
    return False


def _outside_allowed_categories(
    path: str, settings: MCPSettings | None, api_prefix: str
) -> bool:
    """Return whether ``allowed_tool_categories`` leaves out the category of a route path."""
    allowed = getattr(settings, "allowed_tool_categories", None)
    if not allowed or "all" in allowed:
        return False
    return route_naming(path, api_prefix)[0] not in allowed


def process_fastapi_routes_for_mcp(
    app: FastAPI, settings: MCPSettings | None = None
) -> ProcessedRouteData:
    """Build the FastMCP route maps, route lookup, and prompt definitions for every API route of ``app``."""
    processed = ProcessedRouteData()
    typed_route_maps: list[RouteMap] = []
    prompted: list[tuple[APIRoute, str, list[str], str | None]] = []
    api_prefix = get_api_prefix(settings)

    for context in iter_route_contexts(app.router.routes):
        route = context.original_route
        if not isinstance(route, APIRoute):
            continue

        path = cast("str", context.path)
        methods = cast("list[HttpMethod]", sorted(cast("set[str]", route.methods)))
        pattern = f"^{re.escape(path)}$"
        cfg = get_mcp_config(route)

        if (
            cfg.expose is False
            or _should_exclude_by_module_and_path(path, settings)
            or _outside_allowed_categories(path, settings, api_prefix)
        ):
            processed.excluded_routes.append(route)
            processed.route_maps.append(
                RouteMap(pattern=pattern, methods=methods, mcp_type=MCPType.EXCLUDE)
            )
            continue

        configured = _methods_from_config_or_route(cfg, route)
        route_methods = _normalize_methods(methods)
        exposed = [m for m in route_methods if "*" in configured or m in configured]
        dropped = [m for m in route_methods if m not in exposed]
        if dropped:
            processed.route_maps.append(
                RouteMap(
                    pattern=pattern,
                    methods=cast("list[HttpMethod]", dropped),
                    mcp_type=MCPType.EXCLUDE,
                )
            )

        for method in exposed:
            processed.route_lookup[(path, method)] = route
            processed.exposed_methods.setdefault(path, set()).add(method)

        mcp_type_str = cfg.mcp_type.value if cfg.mcp_type else None
        mcp_type = _resolve_mcp_type(mcp_type_str)
        if mcp_type is not None:
            if configured:
                typed_route_maps.append(
                    RouteMap(pattern=pattern, methods=configured, mcp_type=mcp_type)
                )
            else:
                typed_route_maps.append(RouteMap(pattern=pattern, mcp_type=mcp_type))

        if exposed:
            prompted.append((route, path, exposed, cfg.name))

    for route, path, exposed, override in prompted:
        method = "GET" if "GET" in exposed else exposed[0]
        tool_name = tool_name_for_route(
            path, method, api_prefix, processed.exposed_methods, override
        )
        processed.prompt_definitions.extend(
            _create_prompt_definitions_for_route(route, settings, path, tool_name)
        )

    processed.route_maps.extend(typed_route_maps)

    catchall_type = (
        _resolve_mcp_type(getattr(settings, "default_catchall_mcp_type", None))
        or MCPType.TOOL
    )
    processed.route_maps.append(RouteMap(pattern=r".*", mcp_type=catchall_type))

    return processed
