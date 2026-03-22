"""Unit tests for tools module."""

from openbb_mcp_server.models.tools import (
    CategoryInfo,
    SubcategoryInfo,
    ToolInfo,
)


def test_tool_info():
    """Test the ToolInfo model."""
    tool_info = ToolInfo(name="test_tool", active=True, description="A test tool.")
    assert tool_info.name == "test_tool"
    assert tool_info.active is True
    assert tool_info.description == "A test tool."


def test_subcategory_info():
    """Test the SubcategoryInfo model."""
    subcategory_info = SubcategoryInfo(name="test_sub", tool_count=5)
    assert subcategory_info.name == "test_sub"
    assert subcategory_info.tool_count == 5


def test_category_info():
    """Test the CategoryInfo model."""
    subcategories = [SubcategoryInfo(name="sub1", tool_count=2)]
    category_info = CategoryInfo(
        name="test_cat", subcategories=subcategories, total_tools=2
    )
    assert category_info.name == "test_cat"
    assert len(category_info.subcategories) == 1
    assert category_info.total_tools == 2
