"""OpenBB MCP Server."""

# pylint: disable=C0302, R0912, W0212

import asyncio
import json
import os
import re
import signal
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastmcp import FastMCP
from fastmcp.prompts import PromptArgument
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.server.context import Context
from fastmcp.server.providers.openapi import (
    OpenAPIResource,
    OpenAPIResourceTemplate,
    OpenAPITool,
)
from fastmcp.server.providers.skills import (
    ClaudeSkillsProvider,
    CodexSkillsProvider,
    CopilotSkillsProvider,
    CursorSkillsProvider,
    GeminiSkillsProvider,
    GooseSkillsProvider,
    OpenCodeSkillsProvider,
    SkillProvider,
    SkillsDirectoryProvider,
    VSCodeSkillsProvider,
)
from fastmcp.server.transforms import PromptsAsTools, ResourcesAsTools
from fastmcp.utilities.json_schema import compress_schema
from fastmcp.utilities.logging import get_logger
from fastmcp.utilities.openapi import HTTPRoute
from openbb_core.api.rest_api import app
from openbb_core.app.service.system_service import SystemService
from pydantic import Field
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from openbb_mcp_server.models.category_index import CategoryIndex
from openbb_mcp_server.models.mcp_config import (
    ArgumentDefinitionModel,
    is_valid_mcp_config,
)
from openbb_mcp_server.models.prompts import StaticPrompt
from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.models.tools import CategoryInfo, SubcategoryInfo, ToolInfo
from openbb_mcp_server.service.mcp_service import MCPService
from openbb_mcp_server.utils.app_import import parse_args
from openbb_mcp_server.utils.fastapi import (
    get_api_prefix,
    process_fastapi_routes_for_mcp,
)

logger = get_logger(__name__)

_VENDOR_SKILLS_PROVIDERS = {
    "claude": ClaudeSkillsProvider,
    "cursor": CursorSkillsProvider,
    "vscode": VSCodeSkillsProvider,
    "copilot": CopilotSkillsProvider,
    "codex": CodexSkillsProvider,
    "gemini": GeminiSkillsProvider,
    "goose": GooseSkillsProvider,
    "opencode": OpenCodeSkillsProvider,
}


def _extract_brief_description(full_description: str) -> str:
    """Extract only the brief description before the detailed API documentation."""
    if not full_description:
        return "No description available"
    brief, *_ = re.split(
        r"\n{2,}\*\*(?:Query Parameters|Responses):", full_description, maxsplit=1
    )
    return brief.strip() or "No description available"


def _get_mcp_config_from_route(fa_route: APIRoute | None) -> dict:
    """Extract the mcp_config dictionary from a FastAPI route's openapi_extra."""
    if fa_route is None:
        return {}
    extra = fa_route.openapi_extra or {}
    cfg = extra.get("mcp_config") or extra.get("x-mcp") or {}
    if isinstance(cfg, dict):
        return cfg
    return {}


def _strip_api_prefix(path: str, api_prefix: str) -> str:
    """Strip the exact api_prefix (from SystemService) from an absolute path.
    Returns the remainder without a leading slash.
    """
    if not path:
        return ""
    if not path.startswith("/"):
        path = "/" + path
    remainder = (
        path[len(api_prefix) :] if api_prefix and path.startswith(api_prefix) else path
    )
    return remainder.lstrip("/")


def _read_system_prompt_file(file_path: str) -> str | None:
    """Read system prompt content from a text file. Returns None if file doesn't exist or can't be read."""
    try:
        prompt_path = Path(file_path)
        if prompt_path.exists() and prompt_path.is_file():
            return prompt_path.read_text(encoding="utf-8").strip()
    except Exception as e:
        logger.warning("Could not read system prompt file '%s': %s", file_path, e)
    return None


def _build_runtime_middleware() -> list:
    """Build middleware objects compatible with FastMCP.run(middleware=...)."""
    cors = SystemService().system_settings.api_settings.cors

    return [
        Middleware(
            CORSMiddleware,
            allow_origins=cors.allow_origins,
            allow_methods=cors.allow_methods,
            allow_headers=cors.allow_headers,
            allow_credentials=True,
            expose_headers=["Mcp-Session-Id"],
        )
    ]


def _setup_file_system_prompt(mcp: FastMCP, settings: MCPSettings) -> None:
    """Set up system prompt from a file and expose it as a prompt and resource."""
    system_prompt_content = _read_system_prompt_file(settings.system_prompt_file or "")

    if not system_prompt_content:
        return

    def system_prompt_func() -> str:
        """Return the configured system prompt."""
        return system_prompt_content

    mcp.add_prompt(
        FunctionPrompt.from_function(
            system_prompt_func,
            name="system_prompt",
            description="This is the system prompt for the MCP Server."
            + " If you are an agent connected to this server,"
            + " please read this carefully to understand how to interact with, and utilize, the MCP features."
            + " This prompt provides essential guidance and usage instructions"
            + " for effective use of the tools and resources provided by this server.",
            tags={"system"},
        )
    )

    if not mcp.instructions:
        mcp.instructions = system_prompt_content

    @mcp.resource("resource://system_prompt")
    def system_prompt_resource() -> str:
        """Return the system prompt resource content."""
        return system_prompt_func()


def _add_prompts_from_json(mcp: FastMCP, settings: MCPSettings) -> None:
    """Load prompts from server_prompts_file and register them with mcp."""
    if not settings.server_prompts_file:
        return

    try:
        with open(settings.server_prompts_file, encoding="utf-8") as f:
            prompts_json: list = json.load(f) or []
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to load prompts from JSON file: %s", e)
        return

    prompts_added: list = []
    for prompt_def in prompts_json:
        prompt_name = prompt_def.get("name", "")

        if not prompt_name:
            logger.error("Skipping prompt definition without a name: %s", prompt_def)
            continue

        prompt_description = prompt_def.get("description", "")

        if not prompt_description:
            logger.error(
                "Skipping prompt definition without a description: %s", prompt_def
            )
            continue

        prompt_content = prompt_def.get("content", "")

        if not prompt_content:
            logger.error("Skipping prompt definition without content: %s", prompt_def)
            continue

        if not isinstance(prompt_content, str):
            logger.error(
                "Skipping prompt definition with invalid content type. Expected string, got: %s",
                prompt_def,
            )
            continue

        prompt_arguments_def = prompt_def.get("arguments", [])
        arguments: list = []

        argument_defaults: dict = {}

        if prompt_arguments_def:
            for arg in prompt_arguments_def:
                try:
                    validated_arg = ArgumentDefinitionModel(**arg).model_dump(
                        exclude_none=True
                    )
                    arguments.append(
                        PromptArgument(
                            name=validated_arg["name"],
                            description=validated_arg["description"],
                            required="default" not in validated_arg,
                        )
                    )
                    if "default" in validated_arg:
                        argument_defaults[validated_arg["name"]] = validated_arg[
                            "default"
                        ]
                except Exception as e:  # pylint: disable=broad-except
                    logger.error(
                        "Skipping argument definition in server prompt, %s, due to error: %s\nDefinition: %s",
                        prompt_name,
                        e,
                        arg,
                    )
                    continue

        prompt_tags = prompt_def.get("tags", [])
        tags = set(prompt_tags) if isinstance(prompt_tags, (list, set)) else set()
        tags.add("server")
        mcp.add_prompt(
            StaticPrompt(
                name=prompt_name,
                description=prompt_description,
                content=prompt_content,
                arguments=arguments if arguments else None,
                argument_defaults=argument_defaults,
                tags=tags,
            )
        )
        prompts_added.append(prompt_name)

    logger.info("Successfully added %d server prompts.", len(prompts_added))


def _add_inline_prompts(mcp: FastMCP, prompt_definitions: list) -> None:
    """Register inline prompts from route configurations with mcp."""
    inline_prompts_added: list = []
    for prompt_def in prompt_definitions:
        try:
            prompt_name = prompt_def["name"]
            prompt_description = prompt_def["description"]
            prompt_content = prompt_def["content"]
            prompt_arguments_def = prompt_def.get("arguments", [])
            prompt_tags = prompt_def.get("tags", [])
            tool = prompt_def.get("tool", "")

            tags = set(prompt_tags) if isinstance(prompt_tags, (list, set)) else set()
            tags.add("route-specific")
            tags.add(tool)

            arguments = []
            argument_defaults: dict = {}
            for arg in prompt_arguments_def:
                arguments.append(
                    PromptArgument(
                        name=arg["name"],
                        description=arg.get("description"),
                        required="default" not in arg,
                    )
                )
                if "default" in arg:
                    argument_defaults[arg["name"]] = arg["default"]

            mcp.add_prompt(
                StaticPrompt(
                    name=prompt_name,
                    description=prompt_description,
                    arguments=arguments,
                    argument_defaults=argument_defaults,
                    tags=tags,
                    content=prompt_content,
                )
            )
            inline_prompts_added.append(prompt_name)

        except (KeyError, TypeError) as e:
            logger.warning(
                "Skipping invalid prompt definition due to error: %s\nDefinition: %s",
                e,
                prompt_def,
            )
            continue

    if inline_prompts_added:
        logger.info("Successfully added %d inline prompts.", len(inline_prompts_added))


def _add_skills_default_prompt(mcp: FastMCP) -> None:
    """Register a default skills-awareness system prompt when no file prompt is configured."""
    _default_system_content = (
        "This server includes bundled skill guides that teach you how to "
        "use advanced OpenBB Platform capabilities. "
        "Use list_resources() to discover available skills at skill://<name>/SKILL.md URIs."
    )

    def _default_system_prompt() -> str:
        """Return default system prompt content."""
        return _default_system_content

    mcp.add_prompt(
        FunctionPrompt.from_function(
            _default_system_prompt,
            name="system_prompt",
            description=(
                "System prompt with guidance on discovering and using this server's bundled skills and tools."
            ),
            tags={"system"},
        )
    )

    if not mcp.instructions:
        mcp.instructions = _default_system_content

    logger.info("Added default system prompt with skill awareness nudge.")


# pylint: disable=R0914,R0915
def create_mcp_server(
    settings: MCPSettings,
    fastapi_app: FastAPI,
    httpx_kwargs: dict | None = None,
    auth: Any | None = None,
) -> FastMCP:
    """Create and configure the FastMCP server from a FastAPI app instance.

    Parameters
    ----------
    settings: MCPSettings
        The MCPSettings instance containing configuration options for the server.
    fastapi_app: FastAPI
        The FastAPI app instance to be used for the server.
    httpx_kwargs: dict | None
        Optional keyword arguments to pass to the httpx client.
    auth: Any | None
        The authentication provider to use for the server.
        Should be a valid FastMCP.server.auth.AuthProvider instance,
        or an object accepted by the `auth` parameter of FastMCP initialization.

    Returns
    -------
    FastMCP
        The configured FastMCP server instance.
    """
    auth_provider = None
    if auth and isinstance(auth, (list, tuple)) and len(auth) == 2 and all(auth):
        # pylint: disable=import-outside-toplevel
        from .auth import get_auth_provider

        auth_provider = get_auth_provider(settings)

    category_index = CategoryIndex()
    _enabled_tools: set[str] = set()

    # Single-pass processing: filter routes, build route maps, and create lookup dictionary
    processed_data = process_fastapi_routes_for_mcp(fastapi_app, settings)

    route_lookup = processed_data.route_lookup
    api_prefix = get_api_prefix(settings)
    tool_prompts_map: dict = {}

    for prompt_def in processed_data.prompt_definitions:
        tool_name = prompt_def.get("tool")

        if tool_name:
            if tool_name not in tool_prompts_map:
                tool_prompts_map[tool_name] = []
            tool_prompts_map[tool_name].append(
                {
                    "name": prompt_def.get("name"),
                    "description": prompt_def.get("description"),
                    "arguments": prompt_def.get("arguments", []),
                }
            )

    # pylint: disable=R0912
    def customize_components(
        route: HTTPRoute,
        component: OpenAPITool | OpenAPIResource | OpenAPIResourceTemplate,
    ) -> None:
        """Apply naming, tags, enable/disable, and resource mime type using per-route config."""

        # Map back to FastAPI route to read openapi_extra
        fa_route = route_lookup.get((route.path, route.method.upper()))
        mcp_cfg = _get_mcp_config_from_route(fa_route)

        if (exc := is_valid_mcp_config(mcp_cfg)) and isinstance(exc, Exception):
            logger.error(
                "Invalid MCP config found in route, '%s %s'."
                + " Skipping tool customization because of validation error ->\n%s",
                route.method,
                route.path,
                exc,
            )
            mcp_cfg = {}

        # Use the exact API prefix to determine category/subcategory/tool
        local_path = _strip_api_prefix(route.path, api_prefix)
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

        # Name override
        if name := mcp_cfg.get("name"):
            component.name = name
        else:
            component.name = (
                f"{category}_{subcategory}_{tool}"
                if subcategory != "general"
                else f"{category}_{tool}"
            )

        # Tags
        component.tags.add(category)
        extra_tags = mcp_cfg.get("tags") or []
        for t in extra_tags:
            component.tags.add(str(t))

        # Compress schemas (only for OpenAPITool which has these attributes)
        if isinstance(component, OpenAPITool):
            if component.parameters:
                component.parameters = compress_schema(component.parameters)
            if hasattr(component, "output_schema"):
                output_schema = getattr(component, "output_schema", None)
                if output_schema is not None:
                    component.output_schema = compress_schema(output_schema)

        # Description trimming
        describe_override = mcp_cfg.get("describe_responses")
        if describe_override is False or (
            describe_override is None and not settings.describe_responses
        ):
            component.description = _extract_brief_description(
                component.description or ""
            )

        # Add prompt metadata to the tool description
        if isinstance(component, OpenAPITool):
            prompts = tool_prompts_map.get(component.name)
            if prompts:
                prompt_metadata_str = "\n\n**Associated Prompts:**"
                for p in prompts:
                    prompt_metadata_str += f"\n- **{p['name']}**: {p['description']}"
                    if p["arguments"]:
                        prompt_metadata_str += "\n  - Arguments: " + ", ".join(
                            [f"`{arg['name']}`" for arg in p["arguments"]]
                        )
                component.description = (
                    component.description or ""
                ) + prompt_metadata_str

        # Enable/disable: per-route override first, then category defaults
        enable_override = mcp_cfg.get("enable")
        if isinstance(enable_override, bool):
            should_enable = enable_override
        elif "all" in settings.default_tool_categories or any(
            tag in settings.default_tool_categories
            for tag in getattr(component, "tags", set())
        ):
            should_enable = True
        else:
            should_enable = False

        if should_enable and isinstance(component, OpenAPITool):
            _enabled_tools.add(component.name)

        # Resource-specific mime type
        if isinstance(component, OpenAPIResource):
            mime_type = mcp_cfg.get("mime_type")
            if isinstance(mime_type, str) and mime_type:
                component.mime_type = mime_type

        # Register tool in the category index for discovery browsing
        if isinstance(component, OpenAPITool):
            category_index.register(
                category=category,
                subcategory=subcategory,
                tool_name=component.name,
                description=component.description or "",
            )

    # Extract httpx_client_kwargs from settings/kwargs if available
    httpx_client_kwargs = httpx_kwargs or settings.get_httpx_kwargs()

    # Get only FastMCP constructor parameters (excludes uvicorn_config, httpx_client_kwargs)
    fastmcp_kwargs = settings.get_fastmcp_kwargs()

    # Create MCP server from the processed FastAPI app.
    mcp = FastMCP.from_fastapi(
        app=fastapi_app,  # app has been modified in-place
        mcp_component_fn=customize_components,
        route_maps=processed_data.route_maps,
        httpx_client_kwargs=httpx_client_kwargs,
        auth=auth_provider,
        **fastmcp_kwargs,
    )

    # Disable ALL non-admin tools first, then selectively re-enable.
    all_registered = category_index.all_tool_names()
    if all_registered:
        mcp.disable(names=all_registered)

    if settings.enable_tool_discovery:
        # Discovery mode: everything stays disabled.
        # Agents progressively activate what they need per-session
        # via activate_tools / activate_category.
        pass
    elif _enabled_tools:
        # Fixed-toolset mode: re-enable tools that matched
        # per-route overrides or default_tool_categories.
        mcp.enable(names=_enabled_tools)

    # Add system prompt if configured
    if settings.system_prompt_file:
        _setup_file_system_prompt(mcp, settings)

    # Load the prompts json file, if added to the settings configuration.
    _add_prompts_from_json(mcp, settings)

    # Add inline prompts from route configurations
    _add_inline_prompts(mcp, processed_data.prompt_definitions)

    # Load bundled skills via SkillsDirectoryProvider
    _bundled_skills_loaded = False
    if settings.default_skills_dir:
        skills_dir = Path(settings.default_skills_dir)
        if skills_dir.is_dir():
            mcp.add_provider(
                SkillsDirectoryProvider(
                    roots=skills_dir,
                    reload=settings.skills_reload,
                )
            )
            _bundled_skills_loaded = True
            logger.info("Loaded bundled skills from '%s'", skills_dir)

    # Load user-configured vendor skill providers
    if settings.skills_providers:
        for provider_name in settings.skills_providers:
            key = provider_name.lower().strip()
            provider_cls = _VENDOR_SKILLS_PROVIDERS.get(key)
            if provider_cls:
                mcp.add_provider(provider_cls(reload=settings.skills_reload))
                logger.info("Loaded vendor skills provider: '%s'", key)
            else:
                logger.warning(
                    "Unknown skills provider '%s'. Supported: %s",
                    key,
                    ", ".join(_VENDOR_SKILLS_PROVIDERS),
                )

    # If any skills were loaded and no custom system prompt is configured,
    # add a brief default system prompt nudging agents to discover them.
    _skills_loaded = _bundled_skills_loaded or bool(settings.skills_providers)
    if _skills_loaded and not settings.system_prompt_file:
        _add_skills_default_prompt(mcp)

    # Admin/discovery tools if enabled
    if settings.enable_tool_discovery:

        @mcp.tool(tags={"admin"})
        def available_categories() -> list[CategoryInfo]:
            """List available tool categories and subcategories with tool counts."""
            categories = category_index.get_categories()
            return [
                CategoryInfo(
                    name=category_name,
                    subcategories=[
                        SubcategoryInfo(name=subcat_name, tool_count=len(tool_names))
                        for subcat_name, tool_names in sorted(subcategories.items())
                    ],
                    total_tools=sum(
                        len(tool_names) for tool_names in subcategories.values()
                    ),
                )
                for category_name, subcategories in sorted(categories.items())
            ]

        @mcp.tool(tags={"admin"})
        async def available_tools(
            category: Annotated[
                str, Field(description="The category of tools to list")
            ],
            subcategory: Annotated[
                str | None,
                Field(
                    description="Optional subcategory to filter by. "
                    "Use 'general' for tools directly under the category."
                ),
            ] = None,
        ) -> list[ToolInfo]:
            """List tools in a specific category and subcategory."""
            cat_data = category_index.get_subcategories(category)

            if cat_data is None:
                available = list(category_index.get_categories().keys())
                raise ValueError(
                    f"Category '{category}' not found. "
                    f"Available categories: {', '.join(sorted(available))}"
                )

            if subcategory:
                names = category_index.get_subcategory_names(category, subcategory)
                if not names:
                    raise ValueError(
                        f"Subcategory '{subcategory}' not found in category '{category}'. "
                        f"Available subcategories: {', '.join(sorted(cat_data.keys()))}"
                    )
            else:
                names = category_index.get_category_names(category)

            # Resolve active state from FastMCP's live tool list
            active_tools = await mcp.list_tools()
            active_names = {t.name for t in active_tools}

            # Build descriptions — use live tool object when available,
            # fall back to cached short description from the index.
            tool_map = {t.name: t for t in active_tools}
            results: list[ToolInfo] = []
            for name in sorted(names):
                if name in tool_map:
                    desc = _extract_brief_description(tool_map[name].description or "")
                else:
                    desc = category_index.get_description(name)
                results.append(
                    ToolInfo(name=name, active=name in active_names, description=desc)
                )
            return results

        @mcp.tool(tags={"admin"})
        async def activate_tools(
            tool_names: Annotated[
                list[str], Field(description="Names of tools to activate")
            ],
            ctx: Context,
        ) -> str:
            """Activate one or more tools for this session."""
            valid = [n for n in tool_names if category_index.has_tool(n)]
            invalid = [n for n in tool_names if not category_index.has_tool(n)]
            if valid:
                await ctx.enable_components(names=set(valid))
            parts: list[str] = []
            if valid:
                parts.append(f"Activated: {', '.join(valid)}")
            if invalid:
                parts.append(f"Not found: {', '.join(invalid)}")
            return " ".join(parts) or "No tools processed."

        @mcp.tool(tags={"admin"})
        async def deactivate_tools(
            tool_names: Annotated[
                list[str], Field(description="Names of tools to deactivate")
            ],
            ctx: Context,
        ) -> str:
            """Deactivate one or more tools for this session."""
            valid = [n for n in tool_names if category_index.has_tool(n)]
            invalid = [n for n in tool_names if not category_index.has_tool(n)]
            if valid:
                await ctx.disable_components(names=set(valid))
            parts: list[str] = []
            if valid:
                parts.append(f"Deactivated: {', '.join(valid)}")
            if invalid:
                parts.append(f"Not found: {', '.join(invalid)}")
            return " ".join(parts) or "No tools processed."

        @mcp.tool(tags={"admin"})
        async def activate_category(
            category: Annotated[
                str, Field(description="Category name to activate all tools for")
            ],
            ctx: Context,
            subcategory: Annotated[
                str | None,
                Field(description="Optional subcategory to narrow activation"),
            ] = None,
        ) -> str:
            """Activate all tools in a category (or subcategory) for this session."""
            if subcategory:
                names = category_index.get_subcategory_names(category, subcategory)
            else:
                names = category_index.get_category_names(category)
            if not names:
                available = list(category_index.get_categories().keys())
                raise ValueError(
                    f"No tools found in '{category}'"
                    + (f"/'{subcategory}'" if subcategory else "")
                    + f". Available categories: {', '.join(sorted(available))}"
                )
            await ctx.enable_components(names=names)
            scope = f"'{category}'" + (f"/'{subcategory}'" if subcategory else "")
            return (
                f"Activated {len(names)} tools in {scope}"
                f": {', '.join(sorted(names))}"
            )

    # Expose prompts and resources as tools via transforms so that
    # tool-only clients can list/render prompts and list/read resources.
    mcp.add_transform(PromptsAsTools(mcp))
    mcp.add_transform(ResourcesAsTools(mcp))

    @mcp.tool(tags={"resource", "admin"})
    async def install_skill(
        skill_name: Annotated[
            str,
            Field(
                description=(
                    "Name of the skill (used as the directory name). "
                    "Must be a valid directory name (lowercase, underscores)."
                ),
            ),
        ],
        files: Annotated[
            dict[str, str],
            Field(
                description=(
                    "Dictionary of filename -> content for the skill directory. "
                    "Must include 'SKILL.md' as the main file. "
                    "May include supporting files such as templates, examples, "
                    "or configuration snippets (e.g. 'pyproject.toml.template', 'example.py')."
                ),
            ),
        ],
        target: Annotated[
            str,
            Field(
                description=(
                    "Target skills provider to install into. "
                    "Use 'bundled' for the server's built-in skills directory, "
                    "or a vendor name: "
                    + ", ".join(f"'{k}'" for k in _VENDOR_SKILLS_PROVIDERS)
                    + "."
                ),
            ),
        ] = "bundled",
    ) -> dict:
        """Install a skill (SKILL.md + supporting files) into a SkillsDirectoryProvider.

        Creates the skill directory if needed, writes all files,
        and registers the new skill with the target provider so it becomes
        immediately available via list_resources / read_resource.
        """
        if "SKILL.md" not in files:
            raise ValueError(
                "The 'files' dict must include a 'SKILL.md' entry as the main skill file."
            )

        # Find the target SkillsDirectoryProvider
        target_key = target.lower().strip()
        target_provider: SkillsDirectoryProvider | None = None

        for provider in mcp.providers:
            if not isinstance(provider, SkillsDirectoryProvider):
                continue

            if target_key == "bundled":
                if settings.default_skills_dir:
                    bundled_root = Path(settings.default_skills_dir).resolve()
                    if bundled_root in provider._roots:  # noqa: SLF001
                        target_provider = provider
                        break
            else:
                vendor_cls = _VENDOR_SKILLS_PROVIDERS.get(target_key)
                if vendor_cls and isinstance(provider, vendor_cls):
                    target_provider = provider
                    break

        if target_provider is None:
            available = ["bundled"]
            for p in mcp.providers:
                for vendor_name, vendor_cls in _VENDOR_SKILLS_PROVIDERS.items():
                    if isinstance(p, vendor_cls):
                        available.append(vendor_name)
            raise ValueError(
                f"Target provider '{target}' not found or not loaded. "
                f"Available targets: {', '.join(available)}"
            )

        if not target_provider._roots:  # noqa: SLF001
            raise ValueError(
                f"Target provider '{target}' has no configured root directories."
            )

        # Use the first root directory for writing
        root_dir = target_provider._roots[0]  # noqa: SLF001
        skill_dir = root_dir / skill_name

        # Create the directory and write all files
        skill_dir.mkdir(parents=True, exist_ok=True)
        written_files: list[str] = []
        for filename, content in files.items():
            file_path = skill_dir / filename
            # Create subdirectories if the filename contains path separators
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            written_files.append(filename)

        # Register the new skill with the provider
        already_loaded = {
            p._skill_path.name  # noqa: SLF001
            for p in target_provider.providers
            if hasattr(p, "_skill_path")
        }

        if skill_name not in already_loaded:
            new_skill_provider = SkillProvider(skill_path=skill_dir)
            target_provider.providers.append(new_skill_provider)
            action = "Installed"
        else:
            # Skill already exists — re-discover to pick up changed content
            target_provider._discover_skills()  # noqa: SLF001
            action = "Updated"

        logger.info(
            "%s skill '%s' (%d files) in %s provider (root: %s)",
            action,
            skill_name,
            len(written_files),
            target,
            root_dir,
        )

        return {
            "status": action.lower(),
            "skill_name": skill_name,
            "target": target,
            "path": str(skill_dir),
            "files_written": written_files,
            "uri": f"skill://{skill_name}/SKILL.md",
        }

    return mcp


class SSEShutdownWrapper:
    """ASGI middleware to handle SSE connection shutdown gracefully."""

    def __init__(self, asgi_app: ASGIApp):
        """Initialize the SSEShutdownWrapper."""
        self.asgi_app = asgi_app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle incoming ASGI requests."""
        if scope["type"] != "http":
            await self.asgi_app(scope, receive, send)
            return

        # Check if this is an SSE endpoint
        path = scope.get("path", "")

        if not path.endswith("/sse/"):
            await self.asgi_app(scope, receive, send)
            return

        # Wrap send to handle shutdown gracefully
        response_started = False

        async def safe_send(message):
            """Wrap the send function to handle shutdown gracefully."""
            nonlocal response_started

            try:
                if message["type"] == "http.response.start":
                    response_started = True
                    await send(message)
                elif message["type"] == "http.response.body":
                    await send(message)
            except (ConnectionResetError, ConnectionAbortedError):
                # Client disconnected, ignore
                pass
            except RuntimeError as e:
                if "Expected ASGI message" in str(e):
                    # ASGI protocol violation during shutdown, handle gracefully
                    if not response_started:
                        # Send a proper response start if we haven't yet
                        await send(
                            {
                                "type": "http.response.start",
                                "status": 200,
                                "headers": [(b"content-type", b"text/plain")],
                            }
                        )
                        await send(
                            {
                                "type": "http.response.body",
                                "body": b"Connection closed",
                                "more_body": False,
                            }
                        )
                else:
                    raise

        await self.asgi_app(scope, receive, safe_send)


async def stdio_main(mcp_server):
    """Run the MCP server in STDIO mode with signal handling."""
    loop = asyncio.get_running_loop()

    def signal_handler():
        """Signal handler to exit the process immediately."""
        logger.info("Shutdown signal received. Terminating process.")
        os._exit(0)  # pylint: disable=protected-access

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    logger.info("Starting OpenBB MCP Server in STDIO mode. Press Ctrl+C to stop.")

    await loop.run_in_executor(None, mcp_server.run, "stdio")


def main():
    """Start the OpenBB MCP server with enhanced FastAPI app import capabilities."""
    args = parse_args()
    mcp_service = MCPService()
    # Collect all command-line overrides from parsed args
    cli_overrides = args.uvicorn_config.copy()
    # Add MCP-specific CLI arguments if they exist
    if hasattr(args, "allowed_categories") and args.allowed_categories:
        cli_overrides["allowed_categories"] = args.allowed_categories

    if hasattr(args, "default_categories") and args.default_categories:
        cli_overrides["default_categories"] = args.default_categories

    if hasattr(args, "no_tool_discovery") and args.no_tool_discovery:
        cli_overrides["no_tool_discovery"] = args.no_tool_discovery

    if hasattr(args, "system_prompt") and args.system_prompt:
        cli_overrides["system_prompt"] = args.system_prompt

    if hasattr(args, "server_prompts") and args.server_prompts:
        cli_overrides["server_prompts"] = args.server_prompts

    # Load settings with proper priority order (CLI > env > config file > defaults)
    settings = mcp_service.load_with_overrides(**cli_overrides)

    try:
        # Use imported app if provided, otherwise default OpenBB app
        target_app = args.imported_app if args.imported_app else app

        # Extract runtime configuration from settings
        http_run_kwargs = settings.get_http_run_kwargs()
        httpx_kwargs = settings.get_httpx_kwargs()

        # Create MCP server with comprehensive configuration
        mcp_server = create_mcp_server(
            settings, target_app, httpx_kwargs, auth=settings.server_auth
        )

        if args.transport == "stdio":
            asyncio.run(stdio_main(mcp_server))
        else:
            cors_middleware = _build_runtime_middleware()

            # Start building arguments mcp.run
            run_kwargs = {
                "transport": args.transport,
                "middleware": cors_middleware,
            }

            # Extract uvicorn settings
            if http_run_kwargs.get("uvicorn_config"):
                uvicorn_config = http_run_kwargs["uvicorn_config"].copy()

                # Pop host and port to pass them as top-level args
                if "host" in uvicorn_config:
                    run_kwargs["host"] = uvicorn_config.pop("host")

                if "port" in uvicorn_config:
                    port = uvicorn_config.pop("port")
                    run_kwargs["port"] = int(port) if isinstance(port, str) else port

                # Pass the rest of the config in the nested dict.
                if uvicorn_config:
                    run_kwargs["uvicorn_config"] = uvicorn_config

            # Add SSE shutdown handling to middleware stack
            cors_middleware.append(Middleware(SSEShutdownWrapper))
            run_kwargs["middleware"] = cors_middleware

            mcp_server.run(**run_kwargs)

    except KeyboardInterrupt:
        logger.info("Shutdown requested via keyboard interrupt.")
        sys.exit(0)
    except Exception as e:
        logger.error("Server error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
