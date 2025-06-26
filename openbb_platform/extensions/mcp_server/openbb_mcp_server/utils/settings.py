"""MCP Server Settings model."""

from typing import List, Optional

from pydantic import BaseModel, Field


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
        default_factory=lambda: ["equity"],
        description="Default active tool categories on startup",
    )
    allowed_tool_categories: Optional[List[str]] = Field(
        default=None,
        description="If set, restricts available tool categories to this list",
    )

    # Tool discovery configuration
    enable_tool_discovery: bool = Field(
        default=True,
        description="""
            Enable tool discovery, allowing the agent to hot-swap tools at runtime.
            Disable for multi-client or fixed toolset deployments.
        """,
    )

    # Response configuration
    describe_responses: bool = Field(
        default=True,
        description="Include response types in tool descriptions",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(f"{k}: {v}" for k, v in self.model_dump().items())
