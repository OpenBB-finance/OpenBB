"""MCP Settings model."""

from typing import List, Optional

from pydantic import BaseModel, Field, computed_field


class MCPSettings(BaseModel):
    """MCP Server settings model."""

    # Basic server configuration
    name: str = Field(
        default="OpenBB MCP",
    )
    description: str = Field(
        default="""All OpenBB REST endpoints exposed as MCP tools. Enables LLM agents
to query financial data, run screeners, and build workflows using
the exact same operations available to REST clients.""",
    )

    # Tool category filtering
    default_tool_categories: List[str] = Field(
        default_factory=lambda: ["mcp"],
        description="Default active tool categories on startup",
    )
    allowed_tool_categories: Optional[List[str]] = Field(
        default=None,
        description="If set, restricts available tool categories to this list",
    )

    # Provider filtering
    require_valid_credentials: bool = Field(
        default=True,
        description="Only allow providers with valid credentials",
    )
    allowed_providers: Optional[List[str]] = Field(
        default=None,
        description="If set, restricts available providers to this list",
    )

    # Tool filtering
    initial_tools: Optional[List[str]] = Field(
        default=None,
        description="Initial tools to activate. If None, only required tools will be active.",
    )
    allowed_tools: Optional[List[str]] = Field(
        default=None,
        description="If set, restricts available tools to this list",
    )

    # Response configuration
    describe_all_responses: bool = Field(
        default=False,
        description="Include all possible response types in tool descriptions",
    )
    describe_full_response_schema: bool = Field(
        default=False,
        description="Include full response schema in tool descriptions",
    )

    @computed_field
    def required_tools(self) -> List[str]:
        """Return the tools that must always be available."""
        return [
            "get_available_tool_categories",
            "activate_tool_categories",
            "get_available_tools",
            "activate_tools",
        ]

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
