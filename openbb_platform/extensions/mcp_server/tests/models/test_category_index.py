"""Unit tests for CategoryIndex."""

# pylint: disable=redefined-outer-name

import pytest

from openbb_mcp_server.models.category_index import CategoryIndex, _first_sentence


@pytest.fixture
def index():
    """Fixture for a CategoryIndex instance."""
    return CategoryIndex()


def test_register(index):
    """Test tool registration populates the index."""
    index.register(
        category="equity",
        subcategory="price",
        tool_name="equity_price_historical",
        description="Get historical prices.",
    )

    cats = index.get_categories()
    assert "equity" in cats
    assert "equity_price_historical" in cats["equity"]["price"]
    assert index.has_tool("equity_price_historical")
    assert index.get_description("equity_price_historical") == "Get historical prices."


def test_get_categories(index):
    """Test getting all categories."""
    index.register(category="cat1", subcategory="sub1", tool_name="tool1")
    index.register(category="cat2", subcategory="sub2", tool_name="tool2")

    categories = index.get_categories()
    assert set(categories.keys()) == {"cat1", "cat2"}
    assert "tool1" in categories["cat1"]["sub1"]


def test_get_category_names(index):
    """Test getting all tool names in a category."""
    index.register(category="cat1", subcategory="sub1", tool_name="tool1")
    index.register(category="cat1", subcategory="sub1", tool_name="tool2")
    index.register(category="cat1", subcategory="sub2", tool_name="tool3")

    names = index.get_category_names("cat1")
    assert names == {"tool1", "tool2", "tool3"}
    assert index.get_category_names("nonexistent") == set()


def test_get_subcategory_names(index):
    """Test getting tool names in a specific subcategory."""
    index.register(category="cat1", subcategory="sub1", tool_name="tool1")
    index.register(category="cat1", subcategory="sub1", tool_name="tool2")
    index.register(category="cat1", subcategory="sub2", tool_name="tool3")

    assert index.get_subcategory_names("cat1", "sub1") == {"tool1", "tool2"}
    assert index.get_subcategory_names("cat1", "sub2") == {"tool3"}
    assert index.get_subcategory_names("cat1", "missing") == set()
    assert index.get_subcategory_names("missing", "sub1") == set()


def test_get_subcategories(index):
    """Test getting subcategories for a category."""
    index.register(category="cat1", subcategory="sub1", tool_name="tool1")
    index.register(category="cat1", subcategory="sub2", tool_name="tool2")

    subs = index.get_subcategories("cat1")
    assert subs is not None
    assert set(subs.keys()) == {"sub1", "sub2"}
    assert index.get_subcategories("nonexistent") is None


def test_all_tool_names(index):
    """Test getting all registered tool names."""
    index.register(category="cat1", subcategory="sub1", tool_name="tool1")
    index.register(category="cat2", subcategory="sub2", tool_name="tool2")

    assert index.all_tool_names() == {"tool1", "tool2"}


def test_has_tool(index):
    """Test checking if a tool exists."""
    index.register(category="cat", subcategory="sub", tool_name="test")
    assert index.has_tool("test") is True
    assert index.has_tool("nonexistent") is False


def test_clear(index):
    """Test clearing the index."""
    index.register(category="cat", subcategory="sub", tool_name="test", description="d")
    index.clear()
    assert index.get_categories() == {}
    assert index.all_tool_names() == set()
    assert index.has_tool("test") is False
    assert index.get_description("test") == "No description available"


def test_get_description_returns_fallback(index):
    """get_description returns fallback for unknown tools."""
    assert index.get_description("nonexistent") == "No description available"


def test_get_description_extracts_first_sentence(index):
    """Descriptions stored in the index are trimmed to the first sentence."""
    index.register(
        category="equity",
        subcategory="price",
        tool_name="t1",
        description="Get historical prices.\n\nThis returns OHLCV data.",
    )
    assert index.get_description("t1") == "Get historical prices."


def test_get_description_strips_api_sections(index):
    """API doc sections are stripped before extracting the first sentence."""
    index.register(
        category="equity",
        subcategory="price",
        tool_name="t2",
        description="Get quotes.\n\n**Query Parameters:\n- symbol: str",
    )
    assert index.get_description("t2") == "Get quotes."


# ------------------------------------------------------------------
# _first_sentence unit tests
# ------------------------------------------------------------------


class TestFirstSentence:
    """Tests for the _first_sentence helper."""

    def test_empty(self):
        assert _first_sentence("") == ""

    def test_single_sentence(self):
        assert _first_sentence("Get prices.") == "Get prices."

    def test_two_sentences(self):
        assert _first_sentence("Get prices. Supports many params.") == "Get prices."

    def test_multiline(self):
        assert _first_sentence("Get prices.\nMore detail.") == "Get prices."

    def test_no_period_returns_first_line(self):
        assert _first_sentence("Get prices\nMore detail") == "Get prices"

    def test_strips_api_docs(self):
        assert (
            _first_sentence("Get prices.\n\n**Query Parameters:\n- symbol")
            == "Get prices."
        )

    def test_none_like(self):
        assert _first_sentence(None) == ""  # type: ignore[arg-type]
