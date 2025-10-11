"""Utilities for handling FastAPI routes."""

import inspect
import re
import sys
from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastmcp.server.openapi import MCPType, RouteMap
from openbb_core.app.service.system_service import SystemService
from pydantic import ValidationError

from openbb_mcp_server.models.mcp_config import MCPConfigModel, validate_mcp_config
from openbb_mcp_server.models.settings import MCPSettings


class ProcessedRouteData:
    """Container for all data collected during route processing."""

    def __init__(self):
        """Initialize with empty lists and dictionaries."""
        self.route_maps: list[RouteMap] = []
        self.route_lookup: dict[tuple[str, str], APIRoute] = {}
        self.removed_routes: list[APIRoute] = []
        self.prompt_definitions: list[dict] = []


def get_api_prefix(settings: MCPSettings | None) -> str:
    """Get normalized API prefix (leading slash, no trailing slash). Prefer settings.api_prefix if present."""
    override = getattr(settings, "api_prefix", None)
    if isinstance(override, str) and override.strip():
        prefix = override
    else:
        prefix = SystemService().system_settings.api_settings.prefix or ""
    prefix = "/" + prefix.lstrip("/")
    if prefix.endswith("/"):
        prefix = prefix[:-1]
    return prefix


def _get_module_exclusion_targets(settings: MCPSettings | None) -> dict[str, str]:
    """Map path segment -> module name. Prefer settings.module_exclusion_map if a dict is provided."""
    override = getattr(settings, "module_exclusion_map", None)
    if isinstance(override, dict) and override:
        # Ensure keys/values are strings
        return {str(k): str(v) for k, v in override.items()}
    return {
        "econometrics": "openbb_econometrics",
        "quantitative": "openbb_quantitative",
        "technical": "openbb_technical",
        "coverage": "openbb_core",
    }


def get_mcp_config(route: APIRoute, *, strict: bool = False) -> MCPConfigModel:
    """
    Read and validate per-route MCP config from openapi_extra.

    Args:
        route: The APIRoute to process.
        strict: If True, raise validation errors. If False, log warnings.

    Returns:
        A validated MCPConfigModel instance.
    """
    extra = route.openapi_extra or {}
    raw_config = extra.get("mcp_config") or extra.get("x-mcp") or {}

    if not isinstance(raw_config, dict):
        if strict:
            raise TypeError("mcp_config must be a dictionary.")
        raw_config = {}

    try:
        return validate_mcp_config(raw_config, strict=strict)
    except (ValidationError, TypeError, ValueError) as e:
        if strict:
            raise e from e
        return MCPConfigModel()


def _get_prompt_configs(route: APIRoute) -> list[dict]:
    """Extract prompt configurations from per-route MCP config.

    Supports a 'prompts' list of dicts.
    Returns a list of prompt configurations.
    """
    mcp_cfg = get_mcp_config(route)
    # Convert PromptConfigModel to dict
    return [p.model_dump() for p in mcp_cfg.prompts] if mcp_cfg.prompts else []


def _create_prompt_definitions_for_route(
    route: APIRoute, settings: MCPSettings | None = None
) -> list[dict]:
    """Create prompt definitions for a route if prompt configs exist."""
    prompt_configs = _get_prompt_configs(route)
    definitions: list[dict] = []

    if not prompt_configs:
        return definitions

    # Get argument definitions from the endpoint's signature
    # This provides the ground truth for parameter names, types, and defaults
    try:
        sig = inspect.signature(route.endpoint)
        endpoint_args = {
            p.name: {
                "name": p.name,
                "type": (
                    p.annotation.__name__
                    if hasattr(p.annotation, "__name__")
                    else "str"
                ),
                "default": p.default if p.default is not p.empty else ...,
            }
            for p in sig.parameters.values()
            if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
        }
    except (ValueError, TypeError):
        # Cannot inspect signature
        endpoint_args = {}

    # Common info for all prompts on this route
    api_prefix = get_api_prefix(settings)
    tool_uri = route.path.replace(api_prefix, "").lstrip("/").replace("/", "_")
    path = route.path or ""
    if not path.startswith("/"):
        path = "/" + path
    remainder = (
        path[len(api_prefix) :] if api_prefix and path.startswith(api_prefix) else path
    )
    local_path = remainder.lstrip("/")
    segments = [seg for seg in local_path.split("/") if seg and "{" not in seg]

    if segments:
        category = segments[0]
        if len(segments) == 1:
            subcategory = "general"
            tool = segments[0]
        elif len(segments) == 2:
            subcategory = "general"
            tool = segments[1]
        else:
            subcategory = segments[1]
            tool = "_".join(segments[2:])
    else:
        category, subcategory, tool = "general", "general", "root"

    for i, prompt_cfg in enumerate(prompt_configs):
        if not prompt_cfg or not prompt_cfg.get("content"):
            continue

        # Generate prompt name
        prompt_name = prompt_cfg.get("name")
        if not prompt_name:
            base_name = (
                f"{category}_{subcategory}_{tool}"
                if subcategory != "general"
                else f"{category}_{tool}"
            )
            # Add index for uniqueness if multiple unnamed prompts exist
            suffix = f"_{i}" if len(prompt_configs) > 1 else ""
            prompt_name = f"{base_name}_prompt{suffix}"

        # Arguments for the prompt can be a combination of endpoint args and custom ones
        final_args: dict = {}
        prompt_arg_defs = {arg["name"]: arg for arg in prompt_cfg.get("arguments", [])}
        content = (
            f"Use the tool, {tool_uri}, to perform the following task.\n\n"
            + prompt_cfg.get("content", "")
        )

        # All variables in the content string are considered arguments for the prompt
        prompt_vars = re.findall(r"\{(\w+)\}", content)

        for var in set(prompt_vars):
            if var in prompt_arg_defs:
                # Use the definition from the prompt's own 'arguments' list
                final_args[var] = prompt_arg_defs[var]
            elif var in endpoint_args:
                # Inherit the definition from the endpoint's signature
                final_args[var] = endpoint_args[var]
            else:
                # Argument is required by prompt but not defined anywhere
                final_args[var] = {"name": var, "type": "str"}

        # Build prompt definition
        prompt_def = {
            "name": prompt_name,
            "description": prompt_cfg.get("description") or f"Prompt for {tool_uri}",
            "content": content,
            "arguments": list(final_args.values()),
            "tool": tool_uri,
        }

        # Add tags, always including the route path
        tags = list(prompt_cfg.get("tags", []))
        if route.path and route.path not in tags:
            tags.insert(0, route.path)
        prompt_def["tags"] = tags

        definitions.append(prompt_def)

    return definitions


def _normalize_methods(methods: Sequence[str] | None) -> list[str]:
    """Uppercase and filter out HEAD/OPTIONS. Return [] if None/empty."""
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
        # Handle the '*' wildcard for all methods
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

    # Normalize path to avoid double slashes annoyance
    if not path.startswith("/"):
        path = "/" + path

    for segment, module_name in targets.items():
        base = f"{api_prefix}/{segment}"
        if path.startswith(base) and module_name in sys.modules:
            return True
    return False


def process_fastapi_routes_for_mcp(
    app: FastAPI, settings: MCPSettings | None = None
) -> ProcessedRouteData:
    """Single-pass processing of FastAPI routes that:

    1. Removes unwanted routes from the app in-place
    2. Builds route maps for FastMCP
    3. Creates route lookup dictionary for customization
    """
    processed = ProcessedRouteData()
    routes_to_keep = []

    for route in app.router.routes:
        if not isinstance(route, APIRoute):
            routes_to_keep.append(route)  # keep non-HTTP routes
            continue

        # Check if route should be excluded
        cfg = get_mcp_config(route)
        should_exclude = False

        # Explicit per-route exposure control
        if cfg.expose is False or _should_exclude_by_module_and_path(
            route.path or "", settings
        ):
            should_exclude = True

        if should_exclude:
            processed.removed_routes.append(route)
            continue

        # Keep the route
        routes_to_keep.append(route)

        # Build route lookup for customization (only for kept routes)
        for method in route.methods or []:
            method_upper = str(method).upper()
            if method_upper not in {"HEAD", "OPTIONS"}:
                processed.route_lookup[(route.path, method_upper)] = route

        # Build route maps for FastMCP (only for routes with explicit mcp_type)
        mcp_type_str = cfg.mcp_type.value if cfg.mcp_type else None
        mcp_type = _resolve_mcp_type(mcp_type_str)
        if mcp_type is not None:
            methods = _methods_from_config_or_route(cfg, route)
            pattern = f"^{re.escape(route.path)}$"
            if methods:
                processed.route_maps.append(
                    RouteMap(pattern=pattern, methods=methods, mcp_type=mcp_type)
                )
            else:
                processed.route_maps.append(
                    RouteMap(pattern=pattern, mcp_type=mcp_type)
                )

        # Collect prompt definitions (only for routes with prompt config)
        prompt_defs = _create_prompt_definitions_for_route(route, settings)
        if prompt_defs:
            processed.prompt_definitions.extend(prompt_defs)

    # Update the app's routes in-place
    app.router.routes = routes_to_keep

    # Add catch-all route map
    catchall_type = (
        _resolve_mcp_type(getattr(settings, "default_catchall_mcp_type", None))
        or MCPType.TOOL
    )
    processed.route_maps.append(RouteMap(pattern=r".*", mcp_type=catchall_type))

    return processed
