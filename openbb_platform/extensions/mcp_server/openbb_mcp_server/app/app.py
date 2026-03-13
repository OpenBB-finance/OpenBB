"""OpenBB MCP Server."""

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
from fastmcp.prompts.prompt import FunctionPrompt, PromptArgument, PromptResult
from fastmcp.server.openapi import (
    OpenAPIResource,
    OpenAPIResourceTemplate,
    OpenAPITool,
)
from fastmcp.utilities.json_schema import compress_schema
from fastmcp.utilities.logging import get_logger
from fastmcp.utilities.openapi import HTTPRoute
from openbb_core.api.rest_api import app
from openbb_core.app.service.system_service import SystemService
from pydantic import Field
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from openbb_mcp_server.models.mcp_config import (
    ArgumentDefinitionModel,
    is_valid_mcp_config,
)
from openbb_mcp_server.models.prompts import StaticPrompt
from openbb_mcp_server.models.registry import ToolRegistry
from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.models.tools import CategoryInfo, SubcategoryInfo, ToolInfo
from openbb_mcp_server.service.mcp_service import MCPService
from openbb_mcp_server.utils.app_import import parse_args
from openbb_mcp_server.utils.fastapi import (
    get_api_prefix,
    process_fastapi_routes_for_mcp,
)

logger = get_logger(__name__)


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

    tool_registry = ToolRegistry()

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
            if enable_override:
                component.enable()
            else:
                component.disable()
        elif "all" in settings.default_tool_categories or any(
            tag in settings.default_tool_categories
            for tag in getattr(component, "tags", set())
        ):
            component.enable()
        else:
            component.disable()

        # Resource-specific mime type
        if isinstance(component, OpenAPIResource):
            mime_type = mcp_cfg.get("mime_type")
            if isinstance(mime_type, str) and mime_type:
                component.mime_type = mime_type

        # Register tools for discovery/toggling
        if isinstance(component, OpenAPITool):
            tool_registry.register_tool(
                category=category,
                subcategory=subcategory,
                tool_name=component.name,
                tool=component,
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

    # Add system prompt if configured
    if settings.system_prompt_file:
        system_prompt_content = _read_system_prompt_file(settings.system_prompt_file)
        if system_prompt_content:

            def system_prompt_func() -> str:
                """System prompt for the OpenBB MCP server."""
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

            @mcp.resource("resource://system_prompt")
            def system_prompt_resource() -> str:
                """System prompt resource for the MCP Server."""
                return system_prompt_func()

    # Load the prompts json file, if added to the settings configuration.
    prompts_json: list = []

    if settings.server_prompts_file:
        try:
            with open(settings.server_prompts_file, encoding="utf-8") as f:
                prompts_json = json.load(f) or []
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to load prompts from JSON file: %s", e)

    if prompts_json:
        prompts_added: list = []
        for prompt_def in prompts_json:
            prompt_name = prompt_def.get("name", "")

            if not prompt_name:
                logger.error(
                    "Skipping prompt definition without a name: %s", prompt_def
                )
                continue

            prompt_description = prompt_def.get("description", "")

            if not prompt_description:
                logger.error(
                    "Skipping prompt definition without a description: %s",
                    prompt_def,
                )
                continue

            prompt_content = prompt_def.get("content", "")

            if not prompt_content:
                logger.error(
                    "Skipping prompt definition without content: %s",
                    prompt_def,
                )
                continue

            if prompt_content and not isinstance(prompt_content, str):
                logger.error(
                    "Skipping prompt definition with invalid content type. Expected string, got: %s",
                    prompt_def,
                )
                continue

            prompt_arguments_def = prompt_def.get("arguments", [])
            arguments: list = []

            if prompt_arguments_def:
                for arg in prompt_arguments_def:
                    try:
                        # Validate the argument definition
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
                    except Exception as e:
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
            static_prompt = StaticPrompt(
                name=prompt_name,
                description=prompt_description,
                content=prompt_content,
                arguments=arguments if arguments else None,
                tags=tags,
            )
            mcp.add_prompt(static_prompt)
            prompts_added.append(prompt_name)

        logger.info("Successfully added %d server prompts.", len(prompts_added))

    # Add inline prompts from route configurations
    inline_prompts_added: list = []
    for prompt_def in processed_data.prompt_definitions:
        try:
            prompt_name = prompt_def["name"]
            prompt_description = prompt_def["description"]
            prompt_content = prompt_def["content"]
            prompt_arguments_def = prompt_def.get("arguments", [])
            prompt_tags = prompt_def.get("tags", [])
            tool = prompt_def.get("tool", "")

            # Ensure tags are a set
            tags = set(prompt_tags) if isinstance(prompt_tags, (list, set)) else set()
            tags.add("route-specific")
            tags.add(tool)

            # Convert argument definitions to PromptArgument objects
            arguments = [
                PromptArgument(
                    name=arg["name"],
                    description=arg.get("description"),
                    required="default" not in arg,
                )
                for arg in prompt_arguments_def
            ]

            # Create and register the static prompt
            static_prompt = StaticPrompt(
                name=prompt_name,
                description=prompt_description,
                arguments=arguments,
                tags=tags,
                content=prompt_content,
                enabled=True,
            )
            mcp.add_prompt(static_prompt)
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

    # Admin/discovery tools if enabled
    if settings.enable_tool_discovery:

        @mcp.tool(tags={"admin"})
        def available_categories() -> list[CategoryInfo]:
            """List available tool categories and subcategories with tool counts."""
            categories = tool_registry.get_categories()
            return [
                CategoryInfo(
                    name=category_name,
                    subcategories=[
                        SubcategoryInfo(name=subcat_name, tool_count=len(tools))
                        for subcat_name, tools in sorted(subcategories.items())
                    ],
                    total_tools=sum(len(tools) for tools in subcategories.values()),
                )
                for category_name, subcategories in sorted(categories.items())
            ]

        @mcp.tool(tags={"admin"})
        def available_tools(
            category: Annotated[
                str, Field(description="The category of tools to list")
            ],
            subcategory: Annotated[
                str | None,
                Field(
                    description="Optional subcategory to filter by. Use 'general' for tools directly under the category."
                ),
            ] = None,
        ) -> list[ToolInfo]:
            """List tools in a specific category and subcategory."""
            category_data = tool_registry.get_category_subcategories(category)

            if not category_data:
                available_categories_names = list(tool_registry.get_categories().keys())
                categories_str = ", ".join(sorted(available_categories_names))
                raise ValueError(
                    f"Category '{category}' not found. Available categories: {categories_str}"
                )

            if subcategory:
                tools_dict = tool_registry.get_category_tools(category, subcategory)
                if not tools_dict:
                    available_subcategories = list(category_data.keys())
                    subcategories_str = ", ".join(sorted(available_subcategories))
                    raise ValueError(
                        f"Subcategory '{subcategory}' not found in category '{category}'. "
                        f"Available subcategories: {subcategories_str}"
                    )

                return [
                    ToolInfo(
                        name=name,
                        active=tool.enabled,
                        description=_extract_brief_description(tool.description or ""),
                    )
                    for name, tool in sorted(tools_dict.items())
                ]

            tools_dict = tool_registry.get_category_tools(category)

            return [
                ToolInfo(
                    name=name,
                    active=tool.enabled,
                    description=_extract_brief_description(tool.description or ""),
                )
                for name, tool in sorted(tools_dict.items())
            ]

        @mcp.tool(tags={"admin"})
        def activate_tools(
            tool_names: Annotated[
                list[str], Field(description="Names of tools to activate")
            ],
        ) -> str:
            """Activate a tool for use."""
            return tool_registry.toggle_tools(tool_names, enable=True).message

        @mcp.tool(tags={"admin"})
        def deactivate_tools(
            tool_names: Annotated[
                list[str], Field(description="Names of tools to deactivate")
            ],
        ) -> str:
            """Deactivate a tool for use."""
            return tool_registry.toggle_tools(tool_names, enable=False).message

    # Add tools for prompt execution

    @mcp.tool(tags={"prompt"})
    async def list_prompts() -> list:
        """List all available prompts."""
        prompts = await mcp.get_prompts()

        return [
            {"name": p.name, "tags": p.tags, "arguments": p.arguments}
            for p in prompts.values()
        ]

    @mcp.tool(tags={"prompt"})
    async def execute_prompt(
        prompt_name: Annotated[
            str, Field(description="The name of the prompt to execute.")
        ],
        arguments: Annotated[
            dict,
            Field(description="The arguments for the prompt.", default_factory=dict),
        ],
    ) -> PromptResult:
        """Execute a prompt by name."""
        # Find the prompt definition to access default values for arguments
        prompt_def = next(
            (p for p in prompts_json if p.get("name") == prompt_name),
            None,
        )

        if not prompt_def:
            prompt_def = next(
                (
                    p
                    for p in processed_data.prompt_definitions
                    if p.get("name") == prompt_name
                ),
                None,
            )

        # If we found the definition, process arguments to include defaults
        if prompt_def:
            processed_args = arguments.copy()
            prompt_arguments_def = prompt_def.get("arguments", [])
            provided_arg_names = set(processed_args.keys())

            for arg_def in prompt_arguments_def:
                arg_name = arg_def.get("name")
                if (
                    "default" in arg_def
                    and arg_name
                    and arg_name not in provided_arg_names
                ):
                    processed_args[arg_name] = arg_def["default"]

            return await mcp._prompt_manager.render_prompt(  # pylint: disable=protected-access
                name=prompt_name, arguments=processed_args
            )  # type: ignore

        return (
            await mcp._prompt_manager.render_prompt(  # pylint: disable=protected-access
                name=prompt_name, arguments=arguments
            )
        )  # type: ignore

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
