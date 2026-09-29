"""Tests for stateless tool discovery."""

import json

import pytest
from fastapi import APIRouter, FastAPI
from fastmcp import Client
from fastmcp.exceptions import ToolError

from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.app.discovery import OpenBBToolCatalog
from openbb_mcp_server.models.category_index import CategoryIndex
from openbb_mcp_server.models.settings import MCPSettings

ROUTE_TOOLS = {"equity_price_quote", "equity_price_historical", "economy_gdp"}


def _fastapi_app() -> FastAPI:
    api = FastAPI()

    @api.get("/api/v1/equity/price/quote")
    async def quote(symbol: str = "AAPL") -> dict:
        """Get the latest quote for a stock."""
        return {"symbol": symbol, "price": 1.0}

    @api.get("/api/v1/equity/price/historical")
    async def historical(symbol: str = "AAPL") -> dict:
        """Get historical OHLCV prices for a stock."""
        return {"symbol": symbol, "close": [1.0, 2.0]}

    @api.get("/api/v1/economy/gdp")
    async def gdp(country: str = "united_states") -> dict:
        """Get gross domestic product by country."""
        return {"country": country, "gdp": 2.0}

    return api


def _server(*, discovery: bool, api: FastAPI | None = None):
    settings = MCPSettings(
        api_prefix="/api/v1",
        enable_tool_discovery=discovery,
        default_skills_dir=None,
        enable_cli_tools=False,
    )
    return create_mcp_server(settings, _fastapi_app() if api is None else api)


def _structured(result) -> object:
    return json.loads(result.content[0].text)


class TestDiscoveryListing:
    """Discovery mode keeps the OpenBB route tools out of ``list_tools``."""

    @pytest.mark.asyncio
    async def test_route_tools_are_hidden(self):
        async with Client(_server(discovery=True)) as client:
            names = {tool.name for tool in await client.list_tools()}
        assert names.isdisjoint(ROUTE_TOOLS)

    @pytest.mark.asyncio
    async def test_discovery_and_admin_tools_are_listed(self):
        async with Client(_server(discovery=True)) as client:
            names = {tool.name for tool in await client.list_tools()}
        assert {
            "available_categories",
            "available_tools",
            "search_tools",
            "call_tool",
            "install_skill",
            "run_pipeline",
            "list_prompts",
            "get_prompt",
            "list_resources",
            "read_resource",
        } <= names

    @pytest.mark.asyncio
    async def test_session_activation_tools_are_gone(self):
        async with Client(_server(discovery=True)) as client:
            names = {tool.name for tool in await client.list_tools()}
        assert names.isdisjoint(
            {"activate_tools", "activate_category", "deactivate_tools"}
        )

    @pytest.mark.asyncio
    async def test_every_client_sees_the_same_tools(self):
        server = _server(discovery=True)
        async with Client(server) as first:
            await first.call_tool("call_tool", {"name": "economy_gdp"})
            first_names = {tool.name for tool in await first.list_tools()}
        async with Client(server) as second:
            second_names = {tool.name for tool in await second.list_tools()}
        assert first_names == second_names


class TestDiscoverySearch:
    """``search_tools`` searches only the OpenBB route tools."""

    @pytest.mark.asyncio
    async def test_search_returns_matching_route_tool_definitions(self):
        async with Client(_server(discovery=True)) as client:
            result = await client.call_tool("search_tools", {"query": "gdp country"})
        tools = result.structured_content["result"]
        assert tools[0]["name"] == "economy_gdp"
        assert "country" in tools[0]["inputSchema"]["properties"]

    @pytest.mark.asyncio
    async def test_search_excludes_listed_tools(self):
        async with Client(_server(discovery=True)) as client:
            result = await client.call_tool(
                "search_tools", {"query": "stock install skill categories"}
            )
        names = {tool["name"] for tool in result.structured_content["result"]}
        assert names == {"equity_price_quote", "equity_price_historical"}


class TestDiscoveryExecution:
    """Hidden route tools stay callable without any session state."""

    @pytest.mark.asyncio
    async def test_call_tool_proxy_runs_a_hidden_tool(self):
        async with Client(_server(discovery=True)) as client:
            result = await client.call_tool(
                "call_tool",
                {"name": "equity_price_quote", "arguments": {"symbol": "MSFT"}},
            )
        assert _structured(result) == {"symbol": "MSFT", "price": 1.0}

    @pytest.mark.asyncio
    async def test_hidden_tool_is_callable_by_name(self):
        async with Client(_server(discovery=True)) as client:
            result = await client.call_tool("economy_gdp", {"country": "japan"})
        assert _structured(result) == {"country": "japan", "gdp": 2.0}

    @pytest.mark.asyncio
    async def test_call_tool_rejects_unknown_names(self):
        async with Client(_server(discovery=True)) as client:
            with pytest.raises(ToolError, match="Unknown tool"):
                await client.call_tool("call_tool", {"name": "not_a_tool"})


class TestDiscoveryBrowsing:
    """``available_categories`` and ``available_tools`` browse the category index."""

    @pytest.mark.asyncio
    async def test_available_categories(self):
        """Categories are sorted, with per-subcategory and total tool counts."""
        async with Client(_server(discovery=True)) as client:
            result = await client.call_tool("available_categories", {})
        assert result.structured_content["result"] == [
            {
                "name": "economy",
                "subcategories": [{"name": "general", "tool_count": 1}],
                "total_tools": 1,
            },
            {
                "name": "equity",
                "subcategories": [{"name": "price", "tool_count": 2}],
                "total_tools": 2,
            },
        ]

    @pytest.mark.asyncio
    async def test_available_categories_without_routes(self):
        """An app without routes has no categories."""
        async with Client(_server(discovery=True, api=FastAPI())) as client:
            result = await client.call_tool("available_categories", {})
        assert result.structured_content["result"] == []

    @pytest.mark.asyncio
    async def test_available_tools_in_category(self):
        """Without a subcategory every tool in the category is listed."""
        async with Client(_server(discovery=True)) as client:
            result = await client.call_tool("available_tools", {"category": "economy"})
        assert result.structured_content["result"] == [
            {
                "name": "economy_gdp",
                "description": "Get gross domestic product by country.",
            }
        ]

    @pytest.mark.asyncio
    async def test_available_tools_lists_names_and_first_sentences(self):
        """A subcategory lists its tools sorted, each with its first sentence."""
        async with Client(_server(discovery=True)) as client:
            result = await client.call_tool(
                "available_tools", {"category": "equity", "subcategory": "price"}
            )
        assert result.structured_content["result"] == [
            {
                "name": "equity_price_historical",
                "description": "Get historical OHLCV prices for a stock.",
            },
            {
                "name": "equity_price_quote",
                "description": "Get the latest quote for a stock.",
            },
        ]

    @pytest.mark.asyncio
    async def test_available_tools_unknown_category(self):
        """An unknown category names the available ones."""
        async with Client(_server(discovery=True)) as client:
            with pytest.raises(
                ToolError,
                match="Category 'crypto' not found. Available categories: economy, equity",
            ):
                await client.call_tool("available_tools", {"category": "crypto"})

    @pytest.mark.asyncio
    async def test_available_tools_unknown_subcategory(self):
        """An unknown subcategory names the category's subcategories."""
        async with Client(_server(discovery=True)) as client:
            with pytest.raises(
                ToolError,
                match="Subcategory 'options' not found in category 'equity'. Available subcategories: price",
            ):
                await client.call_tool(
                    "available_tools", {"category": "equity", "subcategory": "options"}
                )


class TestFixedToolsetMode:
    """Without discovery the route tools are listed directly."""

    @pytest.mark.asyncio
    async def test_route_tools_are_listed_without_catalog_tools(self):
        async with Client(_server(discovery=False)) as client:
            names = {tool.name for tool in await client.list_tools()}
        assert names >= ROUTE_TOOLS
        assert names.isdisjoint(
            {"search_tools", "call_tool", "available_categories", "available_tools"}
        )


class TestIncludedRouters:
    """Per-route MCP configuration applies to routes of included routers."""

    @pytest.mark.asyncio
    async def test_excluded_route_of_included_router_is_not_a_tool(self):
        """``expose: False`` hides a route that lives in an included router."""
        router = APIRouter(prefix="/admin")

        @router.get("/visible")
        async def visible() -> dict:
            """Visible route."""
            return {}

        @router.get("/hidden", openapi_extra={"mcp_config": {"expose": False}})
        async def hidden() -> dict:
            """Hidden route."""
            return {}

        api = FastAPI()
        api.include_router(router, prefix="/api/v1")
        async with Client(_server(discovery=False, api=api)) as client:
            names = {tool.name for tool in await client.list_tools()}
        assert "admin_visible" in names
        assert "admin_hidden" not in names


class TestOpenBBToolCatalog:
    """Direct checks of the transform's catalog split."""

    @pytest.mark.asyncio
    async def test_transform_tools_removes_only_indexed_tools(self):
        index = CategoryIndex()
        index.register(
            category="economy", subcategory="general", tool_name="economy_gdp"
        )
        tools = await _server(discovery=False).list_tools()
        listed = {
            tool.name for tool in await OpenBBToolCatalog(index).transform_tools(tools)
        }
        assert "economy_gdp" not in listed
        assert {
            "equity_price_quote",
            "equity_price_historical",
            "search_tools",
            "call_tool",
        } <= listed
