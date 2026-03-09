"""Tests for OpenBB code mode utilities."""

# pylint: disable=protected-access
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from openbb_mcp_server.utils.code_mode import (
    OpenBBBM25SearchTransform,
    _render_category_tree_as_markdown,
    build_openbb_code_mode_transform,
    build_openbb_search_transform,
)


@dataclass
class FakeTool:
    """Minimal tool object for search and serialization tests."""

    name: str
    description: str
    parameters: dict[str, Any]
    output_schema: dict[str, Any] | None
    tags: set[str]


@pytest.mark.asyncio
async def test_bm25_search_transform_category_filter() -> None:
    """Test category filtering with explicit categories kwarg."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags={"equity", "price"},
        ),
        FakeTool(
            name="econometrics_panel_first_difference",
            description="First-difference estimate for panel data.",
            parameters={
                "type": "object",
                "properties": {"y_column": {"type": "string"}},
            },
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "object"}},
            },
            tags={"econometrics"},
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    results = await transform.search_tools(tools, "", categories=["econometrics"])

    assert len(results) == 1
    assert results[0].name == "econometrics_panel_first_difference"


@pytest.mark.asyncio
async def test_bm25_search_transform_category_filter_from_name_only() -> None:
    """Category filter works even when tool.tags is empty (inferred from tool name)."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags=set(),  # no tags — category must come from name
        ),
        FakeTool(
            name="economy_indicators",
            description="Get economic indicators.",
            parameters={
                "type": "object",
                "properties": {"country": {"type": "string"}},
            },
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags=set(),
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    results = await transform.search_tools(tools, "", categories=["equity"])

    assert len(results) == 1
    assert results[0].name == "equity_price_historical"


@pytest.mark.asyncio
async def test_bm25_search_transform_tag_filter() -> None:
    """Test subcategory filtering with explicit subcategories kwarg."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags={"equity", "price"},
        ),
        FakeTool(
            name="equity_fundamental_metrics",
            description="Get fundamental metrics.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags={"equity", "fundamental"},
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    results = await transform.search_tools(
        tools, "metrics", subcategories=["fundamental"]
    )

    assert len(results) == 1
    assert results[0].name == "equity_fundamental_metrics"


@pytest.mark.asyncio
async def test_bm25_search_transform_subcategory_filter_from_name_only() -> None:
    """Subcategory filter works even when tool.tags is empty (from tool name)."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags=set(),  # no tags - subcategory must come from name
        ),
        FakeTool(
            name="equity_fundamental_metrics",
            description="Get fundamental metrics.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags=set(),
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    results = await transform.search_tools(
        tools,
        "",
        categories=["equity"],
        subcategories=["price"],
    )

    assert len(results) == 1
    assert results[0].name == "equity_price_historical"


@pytest.mark.asyncio
async def test_bm25_search_transform_provider_filter() -> None:
    """Provider filters match provider tags from tool.tags."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data from Intrinio.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags={"equity", "price", "intrinio"},
        ),
        FakeTool(
            name="equity_price_quote",
            description="Get quotes from FMP.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
            tags={"equity", "price", "fmp"},
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    results = await transform.search_tools(tools, "", providers=["intrinio"])

    assert len(results) == 1
    assert results[0].name == "equity_price_historical"


@pytest.mark.asyncio
async def test_bm25_search_transform_accepts_string_filter_values() -> None:
    """String filter args should work the same as list filter args."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data from Intrinio.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={"type": "object"},
            tags={"equity", "price", "intrinio"},
        ),
        FakeTool(
            name="equity_price_quote",
            description="Get quotes from FMP.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={"type": "object"},
            tags={"equity", "price", "fmp"},
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    results = await transform.search_tools(
        tools,
        "",
        categories="equity",
        subcategories="price",
        providers="intrinio",
    )

    assert len(results) == 1
    assert results[0].name == "equity_price_historical"


@pytest.mark.asyncio
async def test_bm25_search_transform_requested_max_results_is_capped() -> None:
    """Test requested max_results is capped by configured transform limit."""
    tools = [
        FakeTool(
            name=f"equity_price_tool_{i}",
            description="Price tool.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={"type": "object"},
            tags={"equity", "price"},
        )
        for i in range(10)
    ]

    transform = OpenBBBM25SearchTransform(max_results=3)
    results = await transform.search_tools(
        tools,
        "",
        categories=["equity"],
        requested_max_results=8,
    )

    assert len(results) == 3


@pytest.mark.asyncio
async def test_bm25_search_transform_requested_max_results_lower_than_cap() -> None:
    """Test requested max_results can be lower than configured cap."""
    tools = [
        FakeTool(
            name=f"equity_price_tool_{i}",
            description="Price tool.",
            parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
            output_schema={"type": "object"},
            tags={"equity", "price"},
        )
        for i in range(10)
    ]

    transform = OpenBBBM25SearchTransform(max_results=30)
    results = await transform.search_tools(
        tools,
        "",
        categories=["equity"],
        requested_max_results=5,
    )

    assert len(results) == 5


def test_list_categories_nested_counts() -> None:
    """list_categories returns nested category/subcategory counts."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags=set(),
        ),
        FakeTool(
            name="equity_price_quote",
            description="Get latest quote.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags=set(),
        ),
        FakeTool(
            name="equity_fundamental_metrics",
            description="Get fundamental metrics.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags=set(),
        ),
        FakeTool(
            name="crypto_price_historical",
            description="Get crypto historical price data.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags=set(),
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    rows = transform.list_categories(tools)

    # equity has 3 tools, crypto has 1 → equity comes first
    assert rows[0]["category"] == "equity"
    assert rows[0]["tool_count"] == 3
    assert rows[1]["category"] == "crypto"
    assert rows[1]["tool_count"] == 1

    # equity subcategories: price (2), fundamental (1)
    equity_subs = {s["subcategory"]: s["tool_count"] for s in rows[0]["subcategories"]}
    assert equity_subs["price"] == 2
    assert equity_subs["fundamental"] == 1


def test_list_categories_accepts_string_filters() -> None:
    """Category listing accepts string filter args for convenience."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags={"equity", "price"},
        ),
        FakeTool(
            name="crypto_price_historical",
            description="Get crypto historical price data.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags={"crypto", "price"},
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    rows = transform.list_categories(tools, categories="equity")

    assert len(rows) == 1
    assert rows[0]["category"] == "equity"
    assert rows[0]["tool_count"] == 1


def test_render_category_tree_as_markdown() -> None:
    """Nested category tree renders correctly as markdown."""
    rows = [
        {
            "category": "equity",
            "tool_count": 3,
            "subcategories": [
                {"subcategory": "price", "tool_count": 2},
                {"subcategory": "fundamental", "tool_count": 1},
            ],
        },
        {"category": "crypto", "tool_count": 1, "subcategories": []},
    ]
    rendered = _render_category_tree_as_markdown(rows)

    assert "### Categories" in rendered
    assert "`equity` (3 tools)" in rendered
    assert "`price` (2 tools)" in rendered
    assert "`fundamental` (1 tools)" in rendered
    assert "`crypto` (1 tools)" in rendered


@pytest.mark.asyncio
async def test_bm25_index_stable_across_filter_changes() -> None:
    """BM25 index is not rebuilt when only the filter changes."""
    tools = [
        FakeTool(
            name="equity_price_historical",
            description="Get historical price data.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags={"equity"},
        ),
        FakeTool(
            name="crypto_price_historical",
            description="Get crypto price data.",
            parameters={"type": "object"},
            output_schema={"type": "object"},
            tags={"crypto"},
        ),
    ]

    transform = OpenBBBM25SearchTransform(max_results=5)
    await transform.search_tools(tools, "price", categories="equity")
    hash_after_first = (
        transform._bm25_hash
    )  # noqa: SLF001  # pylint: disable=protected-access

    await transform.search_tools(tools, "price", categories="crypto")
    hash_after_second = (
        transform._bm25_hash
    )  # noqa: SLF001  # pylint: disable=protected-access

    assert (
        hash_after_first == hash_after_second
    ), "BM25 hash should be identical — index must not rebuild on filter change"


@pytest.mark.asyncio
async def test_build_openbb_code_mode_transform_uses_three_step_flow() -> None:
    """CodeMode builder exposes list_categories -> search -> get_schema -> execute."""
    transform = build_openbb_code_mode_transform(
        sandbox_provider=object(),
        search_max_results=7,
        search_output_format="markdown",
        execute_tool_name="execute",
    )

    tools = await transform.transform_tools([])
    names = {tool.name for tool in tools}
    assert names == {"list_categories", "search", "get_schema", "execute"}


@pytest.mark.asyncio
async def test_build_openbb_search_transform_uses_standalone_search_mode() -> None:
    """Standalone search builder returns BM25 search transform with OpenBB names and list_categories."""
    transform = build_openbb_search_transform(
        max_results=9,
        output_format="json",
        search_tool_name="search",
        call_tool_name="call_tool",
    )

    assert isinstance(transform, OpenBBBM25SearchTransform)
    assert (
        transform._max_results == 9
    )  # noqa: SLF001  # pylint: disable=protected-access
    assert (
        transform._search_tool_name == "search"
    )  # noqa: SLF001  # pylint: disable=protected-access
    assert (
        transform._call_tool_name == "call_tool"
    )  # noqa: SLF001  # pylint: disable=protected-access
    assert (
        transform._list_categories_tool_name == "list_categories"
    )  # noqa: SLF001  # pylint: disable=protected-access

    tools = await transform.transform_tools([])
    names = {tool.name for tool in tools}
    assert names == {"list_categories", "get_schema", "search", "call_tool"}
