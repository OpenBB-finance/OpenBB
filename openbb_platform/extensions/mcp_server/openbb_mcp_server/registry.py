"""Tool registry for managing MCP tools and tool discovery."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Mapping

from fastmcp.server.openapi import OpenAPITool

from .tool_models import ToggleResult


@dataclass
class ToolRegistry:
    """Keeps track of categories, subcategories and tool instances."""

    _by_category: dict[str, dict[str, dict[str, OpenAPITool]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(dict))
    )
    _by_name: dict[str, OpenAPITool] = field(default_factory=dict)

    def register_tool(
        self, *, category: str, subcategory: str, tool_name: str, tool: OpenAPITool
    ) -> None:
        """Register a tool in the registry."""
        self._by_category[category][subcategory][tool_name] = tool
        self._by_name[tool_name] = tool

    def get_categories(self) -> Mapping[str, Mapping[str, Mapping[str, OpenAPITool]]]:
        """Get immutable view of all categories and their tools."""
        return self._by_category

    def get_category_tools(
        self, category: str, subcategory: str | None = None
    ) -> dict[str, OpenAPITool]:
        """Get tools in a category, optionally filtered by subcategory."""
        if subcategory is None:
            # flatten all subcategories
            return {
                name: tool
                for subcat_tools in self._by_category.get(category, {}).values()
                for name, tool in subcat_tools.items()
            }
        return self._by_category.get(category, {}).get(subcategory, {})

    def get_tool(self, tool_name: str) -> OpenAPITool | None:
        """Get a tool by name."""
        return self._by_name.get(tool_name)

    def get_category_subcategories(
        self, category: str
    ) -> dict[str, dict[str, OpenAPITool]] | None:
        """Get all subcategories for a specific category."""
        return self._by_category.get(category)

    def toggle_tools(self, tool_names: list[str], enable: bool) -> ToggleResult:
        """Enable or disable a list of tools, returning a status message."""
        successful, failed = [], []

        for name in tool_names:
            tool = self._by_name.get(name)
            if tool:
                (tool.enable if enable else tool.disable)()
                successful.append(name)
            else:
                failed.append(name)

        action = "activated" if enable else "deactivated"
        parts: list[str] = []

        if successful:
            parts.append(f"{action.capitalize()}: {', '.join(successful)}")
        if failed:
            parts.append(f"Not found: {', '.join(failed)}")

        message = " ".join(parts) if parts else "No tools processed."

        return ToggleResult(
            action=action,
            successful=successful,
            failed=failed,
            message=message,
        )

    def clear(self) -> None:
        """Clear the registry."""
        self._by_category.clear()
        self._by_name.clear()
