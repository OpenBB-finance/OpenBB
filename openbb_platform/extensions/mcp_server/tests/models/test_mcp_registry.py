"""Unit tests for ToolRegistry."""

# pylint: disable=redefined-outer-name
from unittest.mock import MagicMock

import pytest
from fastmcp.server.openapi import OpenAPITool
from fastmcp.utilities.openapi import HTTPRoute
from openbb_mcp_server.models.registry import ToolRegistry
from openbb_mcp_server.models.tools import ToggleResult


@pytest.fixture
def tool_registry():
    """Fixture for a ToolRegistry instance."""
    return ToolRegistry()


def test_register_tool(tool_registry):
    """Test tool registration."""
    tool = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy", method="GET"),
        name="test_tool",
        description="Test",
        parameters={},
    )
    tool_registry.register_tool(
        category="test_cat", subcategory="test_sub", tool_name="test_tool", tool=tool
    )

    assert "test_cat" in tool_registry.get_categories()
    assert "test_tool" in tool_registry.get_category_tools("test_cat", "test_sub")
    assert tool_registry.get_tool("test_tool") == tool


def test_get_categories(tool_registry):
    """Test getting all categories."""
    tool1 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy1", method="GET"),
        name="tool1",
        description="Tool1",
        parameters={},
    )
    tool2 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy2", method="GET"),
        name="tool2",
        description="Tool2",
        parameters={},
    )

    tool_registry.register_tool(
        category="cat1", subcategory="sub1", tool_name="tool1", tool=tool1
    )
    tool_registry.register_tool(
        category="cat2", subcategory="sub2", tool_name="tool2", tool=tool2
    )

    categories = tool_registry.get_categories()
    assert set(categories.keys()) == {"cat1", "cat2"}
    assert "sub1" in categories["cat1"]
    assert "tool1" in categories["cat1"]["sub1"]


def test_get_category_tools(tool_registry):
    """Test getting tools from a category."""
    tool1 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy1", method="GET"),
        name="tool1",
        description="Tool1",
        parameters={},
    )
    tool2 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy2", method="GET"),
        name="tool2",
        description="Tool2",
        parameters={},
    )
    tool3 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy3", method="GET"),
        name="tool3",
        description="Tool3",
        parameters={},
    )

    tool_registry.register_tool(
        category="cat1", subcategory="sub1", tool_name="tool1", tool=tool1
    )
    tool_registry.register_tool(
        category="cat1", subcategory="sub1", tool_name="tool2", tool=tool2
    )
    tool_registry.register_tool(
        category="cat1", subcategory="sub2", tool_name="tool3", tool=tool3
    )

    # Specific subcategory
    tools_sub1 = tool_registry.get_category_tools("cat1", "sub1")
    assert set(tools_sub1.keys()) == {"tool1", "tool2"}

    # All subcategories
    all_tools = tool_registry.get_category_tools("cat1")
    assert set(all_tools.keys()) == {"tool1", "tool2", "tool3"}

    # Non-existent
    assert tool_registry.get_category_tools("nonexistent") == {}


def test_get_tool(tool_registry):
    """Test getting a single tool by name."""
    tool = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy", method="GET"),
        name="test",
        description="Test",
        parameters={},
    )
    tool_registry.register_tool(
        category="cat", subcategory="sub", tool_name="test", tool=tool
    )

    assert tool_registry.get_tool("test") == tool
    assert tool_registry.get_tool("nonexistent") is None


def test_get_category_subcategories(tool_registry):
    """Test getting subcategories for a category."""
    tool1 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy1", method="GET"),
        name="tool1",
        description="Tool1",
        parameters={},
    )
    tool2 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy2", method="GET"),
        name="tool2",
        description="Tool2",
        parameters={},
    )
    tool_registry.register_tool(
        category="cat1", subcategory="sub1", tool_name="tool1", tool=tool1
    )
    tool_registry.register_tool(
        category="cat1", subcategory="sub2", tool_name="tool2", tool=tool2
    )

    subcategories = tool_registry.get_category_subcategories("cat1")
    assert subcategories is not None
    assert set(subcategories.keys()) == {"sub1", "sub2"}
    assert "tool1" in subcategories["sub1"]
    assert "tool2" in subcategories["sub2"]
    assert tool_registry.get_category_subcategories("nonexistent") is None


def test_toggle_tools(tool_registry):
    """Test enabling and disabling tools."""
    tool1 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy1", method="GET"),
        name="tool1",
        description="Tool1",
        parameters={},
    )
    tool2 = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy2", method="GET"),
        name="tool2",
        description="Tool2",
        parameters={},
    )

    tool_registry.register_tool(
        category="cat", subcategory="sub", tool_name="tool1", tool=tool1
    )
    tool_registry.register_tool(
        category="cat", subcategory="sub", tool_name="tool2", tool=tool2
    )

    # Enable
    result = tool_registry.toggle_tools(["tool1", "tool2", "missing"], enable=True)
    assert isinstance(result, ToggleResult)
    assert result.action == "activated"
    assert set(result.successful) == {"tool1", "tool2"}
    assert result.failed == ["missing"]
    assert tool1.enabled
    assert tool2.enabled

    # Disable
    result = tool_registry.toggle_tools(["tool1"], enable=False)
    assert result.action == "deactivated"
    assert result.successful == ["tool1"]
    assert result.failed == []
    assert not tool1.enabled
    assert tool2.enabled  # Still enabled

    # Empty list
    result = tool_registry.toggle_tools([], enable=True)
    assert result.message == "No tools processed."


def test_clear(tool_registry):
    """Test clearing the registry."""
    tool = OpenAPITool(
        MagicMock(),
        HTTPRoute(path="/dummy", method="GET"),
        name="test",
        description="Test",
        parameters={},
    )
    tool_registry.register_tool(
        category="cat", subcategory="sub", tool_name="test", tool=tool
    )

    tool_registry.clear()
    assert tool_registry.get_categories() == {}
    assert tool_registry.get_tool("test") is None
