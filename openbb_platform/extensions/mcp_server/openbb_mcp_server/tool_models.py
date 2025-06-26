"""Tool models for MCP server."""

from typing import List

from pydantic import BaseModel


class ToolInfo(BaseModel):
    name: str
    active: bool
    description: str


class SubcategoryInfo(BaseModel):
    name: str
    tool_count: int


class CategoryInfo(BaseModel):
    name: str
    subcategories: List[SubcategoryInfo]
    total_tools: int


class ToggleResult(BaseModel):
    action: str  # "activated" or "deactivated"
    successful: List[str]
    failed: List[str]
    message: str
