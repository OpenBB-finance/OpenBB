"""Unit tests for ToolRegistry."""

# pylint: disable=redefined-outer-name
import sys
from unittest.mock import MagicMock

import pytest
from fastmcp.server.openapi import OpenAPITool
from openbb_mcp_server.registry import ToolRegistry
from openbb_mcp_server.tool_models import ToggleResult

# Skip all tests if Python version < 3.10
if sys.version_info < (3, 10):
    pytest.skip("MCP server requires Python 3.10+", allow_module_level=True)


@pytest.fixture
def tool_registry():
    return ToolRegistry()


def test_register_tool(tool_registry):
    tool = OpenAPITool(
        MagicMock(), "/dummy", name="test_tool", description="Test", parameters={}
    )
    tool_registry.register_tool(
        category="test_cat", subcategory="test_sub", tool_name="test_tool", tool=tool
    )

    assert "test_cat" in tool_registry.get_categories()
    assert "test_tool" in tool_registry.get_category_tools("test_cat", "test_sub")
    assert tool_registry.get_tool("test_tool") == tool


def test_get_categories(tool_registry):
    tool1 = OpenAPITool(
        MagicMock(), "/dummy1", name="tool1", description="Tool1", parameters={}
    )
    tool2 = OpenAPITool(
        MagicMock(), "/dummy2", name="tool2", description="Tool2", parameters={}
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
    tool1 = OpenAPITool(
        MagicMock(), "/dummy1", name="tool1", description="Tool1", parameters={}
    )
    tool2 = OpenAPITool(
        MagicMock(), "/dummy2", name="tool2", description="Tool2", parameters={}
    )
    tool3 = OpenAPITool(
        MagicMock(), "/dummy3", name="tool3", description="Tool3", parameters={}
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
    tool = OpenAPITool(
        MagicMock(), "/dummy", name="test", description="Test", parameters={}
    )
    tool_registry.register_tool(
        category="cat", subcategory="sub", tool_name="test", tool=tool
    )

    assert tool_registry.get_tool("test") == tool
    assert tool_registry.get_tool("nonexistent") is None


def test_toggle_tools(tool_registry):
    tool1 = OpenAPITool(
        MagicMock(), "/dummy1", name="tool1", description="Tool1", parameters={}
    )
    tool2 = OpenAPITool(
        MagicMock(), "/dummy2", name="tool2", description="Tool2", parameters={}
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


def test_clear(tool_registry):
    tool = OpenAPITool(
        MagicMock(), "/dummy", name="test", description="Test", parameters={}
    )
    tool_registry.register_tool(
        category="cat", subcategory="sub", tool_name="test", tool=tool
    )

    tool_registry.clear()
    assert tool_registry.get_categories() == {}
    assert tool_registry.get_tool("test") is None
