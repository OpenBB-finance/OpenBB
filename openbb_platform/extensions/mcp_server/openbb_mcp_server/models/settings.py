"""MCP Server Settings model."""

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_DEFAULT_SKILLS_DIR = str(Path(__file__).resolve().parent.parent / "skills")

DuplicateBehavior = Literal["warn", "error", "replace", "ignore"]


class MCPSettings(BaseModel):
    """MCP Server settings model."""

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        revalidate_instances="always",
        from_attributes=True,
        extra="allow",
    )

    # ===== Basic OpenBB MCP Configuration =====
    api_prefix: str | None = Field(
        default=None,
        description="If set, overrides the API prefix from SystemService. For testing or special cases.",
        alias="OPENBB_MCP_API_PREFIX",
    )

    # Basic server configuration
    name: str = Field(
        default="OpenBB MCP",
        alias="OPENBB_MCP_NAME",
    )
    description: str = Field(
        default="""All OpenBB REST endpoints exposed as MCP tools. Enables LLM agents
to query financial data, run screeners, and build workflows using
the exact same operations available to REST clients.""",
        alias="OPENBB_MCP_DESCRIPTION",
    )
    version: str | None = Field(
        default=None,
        description="Server version",
        alias="OPENBB_MCP_VERSION",
    )

    # Tool category filtering
    default_tool_categories: list[str] = Field(
        default_factory=lambda: ["all"],
        description="Default active tool categories on startup",
        alias="OPENBB_MCP_DEFAULT_TOOL_CATEGORIES",
    )
    allowed_tool_categories: list[str] | None = Field(
        default=None,
        description="If set, restricts available tool categories to this list",
        alias="OPENBB_MCP_ALLOWED_TOOL_CATEGORIES",
    )

    # Tool discovery configuration
    enable_tool_discovery: bool = Field(
        default=True,
        description="""
            Enable tool discovery, allowing the agent to hot-swap tools at runtime.
            Disable for multi-client or fixed toolset deployments.
        """,
        alias="OPENBB_MCP_ENABLE_TOOL_DISCOVERY",
    )

    # Pagination configuration
    list_page_size: int | None = Field(
        default=None,
        description="Maximum number of tools/resources/prompts returned per page in list responses. "
        "None disables pagination (all items returned in one response).",
        alias="OPENBB_MCP_LIST_PAGE_SIZE",
    )

    # Response configuration
    describe_responses: bool = Field(
        default=False,
        description="Include response types in tool descriptions",
        alias="OPENBB_MCP_DESCRIBE_RESPONSES",
    )

    # Prompt configuration
    instructions: str | None = Field(
        default=None,
        description="Server instructions sent to the agent during the MCP initialize handshake."
        " When set, this text is delivered before any tools or prompts are called."
        " If not explicitly set, it is auto-populated from the system prompt content.",
        alias="OPENBB_MCP_INSTRUCTIONS",
    )

    system_prompt_file: str | None = Field(
        default=None,
        description="Path to a text file containing the system prompt for the server",
        alias="OPENBB_MCP_SYSTEM_PROMPT_FILE",
    )

    server_prompts_file: str | None = Field(
        default=None,
        description="Path to a JSON file containing prompt templates for the server",
        alias="OPENBB_MCP_SERVER_PROMPTS_FILE",
    )

    default_skills_dir: str | None = Field(
        default=_DEFAULT_SKILLS_DIR,
        description="Path to a directory containing bundled skill prompt files (.md/.txt)."
        " Set to None or empty string to disable loading default skills.",
        alias="OPENBB_MCP_DEFAULT_SKILLS_DIR",
    )

    # ===== FastMCP Core Configuration =====

    # Cache configuration
    cache_expiration_seconds: float | None = Field(
        default=None,
        description="Cache expiration time in seconds. set to 0 to disable caching.",
        alias="OPENBB_MCP_CACHE_EXPIRATION_SECONDS",
    )

    # Duplicate handling
    on_duplicate_tools: DuplicateBehavior | None = Field(
        default=None,
        description="Behavior when duplicate tools are registered",
        alias="OPENBB_MCP_ON_DUPLICATE_TOOLS",
    )

    on_duplicate_resources: DuplicateBehavior | None = Field(
        default=None,
        description="Behavior when duplicate resources are registered",
        alias="OPENBB_MCP_ON_DUPLICATE_RESOURCES",
    )

    on_duplicate_prompts: DuplicateBehavior | None = Field(
        default=None,
        description="Behavior when duplicate prompts are registered",
        alias="OPENBB_MCP_ON_DUPLICATE_PROMPTS",
    )

    # Resource and component configuration
    resource_prefix_format: Literal["protocol", "path"] | None = Field(
        default=None,
        description="Format for resource URI prefixes: 'protocol' (prefix+protocol://path) or 'path' (protocol://prefix/path)",
        alias="OPENBB_MCP_RESOURCE_PREFIX_FORMAT",
    )

    mask_error_details: bool | None = Field(
        default=None,
        description="If True, mask error details from user functions before sending to clients",
        alias="OPENBB_MCP_MASK_ERROR_DETAILS",
    )

    dependencies: list[str] | None = Field(
        default=None,
        description="list of dependencies to install in the server environment",
        alias="OPENBB_MCP_DEPENDENCIES",
    )

    skills_reload: bool = Field(
        default=False,
        description="If True, skills providers will reload skill files on every read (useful during development).",
        alias="OPENBB_MCP_SKILLS_RELOAD",
    )

    skills_providers: list[str] | None = Field(
        default=None,
        description="List of vendor skill provider short-names to load (e.g. ['claude', 'cursor']). "
        "Supported: claude, cursor, vscode, copilot, codex, gemini, goose, opencode.",
        alias="OPENBB_MCP_SKILLS_PROVIDERS",
    )

    module_exclusion_map: dict[str, str] | None = Field(
        default=None,
        description="Key:Value pairs mapping API Tags with their Python module names."
        + " Example, {'econometrics': 'openbb_econometrics'}",
        alias="OPENBB_MCP_MODULE_EXCLUSION_MAP",
    )
    deprecation_warnings: bool | None = Field(
        default=False,
        description="If True, show deprecation warnings in the console.",
    )

    # ===== HTTP Transport Configuration =====

    # Uvicorn server configuration
    uvicorn_config: dict[str, Any] | None = Field(
        default_factory=lambda: {"host": "127.0.0.1", "port": "8001"},
        description="Additional configuration object for the Uvicorn server."
        + " All items are passed as kwargs to `mcp.run(uvicorn_config=uvicorn_config)`",
        alias="OPENBB_MCP_UVICORN_CONFIG",
    )

    # HTTP client configuration for outbound requests
    httpx_client_kwargs: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Configuration object for async httpx client used by FastMCP."
        + " Add custom headers as a dictionary under the 'headers' key."
        + " All items passed directly to FastMCP.from_fastapi(httpx_client_kwargs=httpx_client_kwargs)",
        alias="OPENBB_MCP_HTTPX_CLIENT_KWARGS",
    )
    client_auth: tuple[str, str] | None = Field(
        default=None,
        description="""
        A tuple of (username, password) for client-side basic authentication.
        If provided, this will be passed to the httpx client for downstream requests.
        Example: OPENBB_MCP_CLIENT_AUTH='["user","pass"]'
        """,
        alias="OPENBB_MCP_CLIENT_AUTH",
    )
    server_auth: tuple[str, str] | None = Field(
        default=None,
        description="""
        A tuple of (username, password) for server-side basic authentication.
        If provided, the MCP server will require incoming requests to provide these credentials.
        Example: OPENBB_MCP_SERVER_AUTH='["user","pass"]'
        """,
        alias="OPENBB_MCP_SERVER_AUTH",
    )

    @field_validator(
        "default_tool_categories",
        "allowed_tool_categories",
        "dependencies",
        "skills_providers",
        mode="before",
    )
    @classmethod
    def _split_list(cls, v):
        if isinstance(v, str):
            return [part.strip() for part in v.split(",") if part.strip()]
        return v

    @field_validator("httpx_client_kwargs", "client_auth", "server_auth", mode="before")
    @classmethod
    def _validate_json_or_tuple(cls, v):
        """Validate json or tuple."""
        if isinstance(v, str):
            if not v.strip():
                return None
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Fallback for simple string if not valid JSON
                return v
        return v

    def get_fastmcp_kwargs(self) -> dict:
        """
        Extract FastMCP constructor arguments from the settings.

        Returns a dictionary containing only the non-None FastMCP parameters
        that can be passed directly to the FastMCP constructor.
        """
        fastmcp_fields = {
            "name": self.name,
            "instructions": self.instructions,
            "version": self.version,
            "cache_expiration_seconds": self.cache_expiration_seconds,
            "on_duplicate_tools": self.on_duplicate_tools,
            "on_duplicate_resources": self.on_duplicate_resources,
            "on_duplicate_prompts": self.on_duplicate_prompts,
            "resource_prefix_format": self.resource_prefix_format,
            "mask_error_details": self.mask_error_details,
            "dependencies": self.dependencies,
            "list_page_size": self.list_page_size,
        }

        # Only include non-None values
        return {k: v for k, v in fastmcp_fields.items() if v is not None}

    def get_http_run_kwargs(self) -> dict:
        """
        Extract HTTP runtime arguments for FastMCP.run_http_async() method.

        Returns a dictionary containing HTTP transport settings.
        """
        run_fields: dict = {}

        if self.uvicorn_config is not None:
            run_fields["uvicorn_config"] = self.uvicorn_config

        return run_fields

    def get_httpx_kwargs(self) -> dict:
        """
        Extract httpx client configuration.

        Returns a dictionary containing httpx client settings.
        """
        kwargs = self.httpx_client_kwargs or {}
        if self.client_auth:
            kwargs["auth"] = self.client_auth
        return kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    def update(self, incoming: "MCPSettings"):
        """Update current settings."""
        self.__dict__.update(incoming.model_dump(exclude_none=True))
