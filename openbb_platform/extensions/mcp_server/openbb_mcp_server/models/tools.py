"""Tool models for MCP server."""

from typing import Literal

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


class ToggleResult(BaseModel):
    """Result of a request to activate or deactivate one or more tools."""

    action: Literal["activated", "deactivated"]
    successful: list[str]
    failed: list[str]
    message: str
