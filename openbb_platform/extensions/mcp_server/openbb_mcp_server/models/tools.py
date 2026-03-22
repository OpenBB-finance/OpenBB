"""Tool models for MCP server."""

from pydantic import BaseModel


class ToolInfo(BaseModel):
    """Information about a single tool."""

    name: str
    active: bool
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
