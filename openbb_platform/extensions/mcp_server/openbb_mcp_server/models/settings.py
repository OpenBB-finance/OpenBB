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

    api_prefix: str | None = Field(
        default=None,
        description="If set, overrides the API prefix from SystemService. For testing or special cases.",
        alias="OPENBB_MCP_API_PREFIX",
    )

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

    enable_tool_discovery: bool = Field(
        default=False,
        description="Hide the OpenBB tools from the tool list and expose them through"
        + " available_categories, available_tools, search_tools, and call_tool."
        + " Stateless, so every client sees the same tool list.",
        alias="OPENBB_MCP_ENABLE_TOOL_DISCOVERY",
    )

    list_page_size: int | None = Field(
        default=None,
        description="Maximum number of tools/resources/prompts returned per page in list responses. "
        "None disables pagination (all items returned in one response).",
        alias="OPENBB_MCP_LIST_PAGE_SIZE",
    )

    describe_responses: bool = Field(
        default=False,
        description="Include response types in tool descriptions",
        alias="OPENBB_MCP_DESCRIBE_RESPONSES",
    )

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
        description="Directory of bundled skills, one sub-directory per skill with a SKILL.md."
        " Set to None or an empty string to disable the bundled skills.",
        alias="OPENBB_MCP_DEFAULT_SKILLS_DIR",
    )

    on_duplicate: DuplicateBehavior | None = Field(
        default=None,
        description="Behavior when a tool, resource, or prompt is registered twice",
        alias="OPENBB_MCP_ON_DUPLICATE",
    )

    mask_error_details: bool | None = Field(
        default=None,
        description="If True, mask error details from user functions before sending to clients",
        alias="OPENBB_MCP_MASK_ERROR_DETAILS",
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
        description="Route path segments mapped to Python modules; routes under a segment are"
        " hidden while its module is imported. None uses {'coverage': 'openbb_core'};"
        " an empty mapping hides nothing.",
        alias="OPENBB_MCP_MODULE_EXCLUSION_MAP",
    )

    enable_cli_tools: bool = Field(
        default=True,
        description=(
            "If True (default) and ``openbb-cli`` is installed, register"
            " ``openbb_dispatch``, ``openbb_batch_dispatch``, ``openbb_list_commands``,"
            " and ``openbb_describe_command``, which wrap the CLI's"
            " LocalDispatcher / HttpDispatcher protocol. Set to False to"
            " suppress registration even when openbb-cli is available."
        ),
        alias="OPENBB_MCP_ENABLE_CLI_TOOLS",
    )

    uvicorn_config: dict[str, Any] | None = Field(
        default_factory=lambda: {"host": "127.0.0.1", "port": "8001"},
        description="Additional configuration object for the Uvicorn server."
        + " All items are passed as kwargs to `mcp.run(uvicorn_config=uvicorn_config)`",
        alias="OPENBB_MCP_UVICORN_CONFIG",
    )

    httpx_client_kwargs: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Configuration object for async httpx client used by FastMCP."
        + " Add custom headers as a dictionary under the 'headers' key."
        + " All items passed directly to FastMCP.from_fastapi(httpx_client_kwargs=httpx_client_kwargs)",
        alias="OPENBB_MCP_HTTPX_CLIENT_KWARGS",
    )
    client_auth: tuple[str, str] | None = Field(
        default=None,
        description="A (username, password) pair passed as httpx ``auth`` on requests to the"
        ' wrapped API. Example: OPENBB_MCP_CLIENT_AUTH=\'["user","pass"]\'',
        alias="OPENBB_MCP_CLIENT_AUTH",
    )
    server_auth: tuple[str, str] | None = Field(
        default=None,
        description="A (username, password) pair. When set, HTTP requests must carry"
        " ``Authorization: Bearer <base64(username:password)>``."
        ' Example: OPENBB_MCP_SERVER_AUTH=\'["user","pass"]\'',
        alias="OPENBB_MCP_SERVER_AUTH",
    )

    @field_validator(
        "default_tool_categories",
        "allowed_tool_categories",
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
                return v
        return v

    def get_fastmcp_kwargs(self) -> dict:
        """Return the FastMCP constructor arguments that are set."""
        fastmcp_fields = {
            "name": self.name,
            "instructions": self.instructions,
            "version": self.version,
            "on_duplicate": self.on_duplicate,
            "mask_error_details": self.mask_error_details,
            "list_page_size": self.list_page_size,
        }

        return {k: v for k, v in fastmcp_fields.items() if v is not None}

    def get_http_run_kwargs(self) -> dict:
        """Return the HTTP runtime arguments for ``FastMCP.run``."""
        run_fields: dict = {}

        if self.uvicorn_config is not None:
            run_fields["uvicorn_config"] = self.uvicorn_config

        return run_fields

    def get_httpx_kwargs(self) -> dict:
        """Return the httpx client configuration, with ``client_auth`` attached as ``auth``."""
        kwargs = dict(self.httpx_client_kwargs or {})
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
