"""Tool models for MCP server."""

from typing import Any

from pydantic import BaseModel, Field


class ToolInfo(BaseModel):
    """Information about a single tool."""

    name: str
    description: str


class SubcategoryInfo(BaseModel):
    """Metadata for a tool subcategory."""

    name: str
    tool_count: int


class CategoryInfo(BaseModel):
    """Metadata for a category of tools."""

    name: str
    subcategories: list[SubcategoryInfo]
    total_tools: int


class PipelineStep(BaseModel):
    """One tool call in a ``run_pipeline`` request."""

    id: str | None = Field(
        default=None,
        description="Name later steps use in ``inputs`` to refer to this step.",
    )
    tool: str = Field(description="Name of the tool to call.")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Arguments passed to the tool."
    )
    inputs: dict[str, str] = Field(
        default_factory=dict,
        description="Maps an argument name to the ``id`` of an earlier step whose"
        ' ``results`` fill it, e.g. ``{"data": "prices"}``.',
    )
