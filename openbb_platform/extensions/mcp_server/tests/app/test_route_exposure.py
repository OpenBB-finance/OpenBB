"""Tests for which routes a served app exposes as tools, under which names, and with which arguments."""

import pytest
from fastapi import FastAPI, Request
from fastmcp import Client
from fastmcp.exceptions import ToolError
from mcp.shared.exceptions import MCPError

from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings


def _api() -> FastAPI:
    api = FastAPI()

    @api.get(
        "/api/v1/demo/echo",
        openapi_extra={"mcp_config": {"exclude_args": ["internal"]}},
    )
    async def echo(symbol: str, internal: str = "hidden") -> dict:
        """Echo a symbol."""
        return {"symbol": symbol, "internal": internal}

    @api.get(
        "/api/v1/demo/defaults",
        openapi_extra={"mcp_config": {"exclude_args": ["internal"]}},
    )
    async def defaults(symbol: str = "SPY", internal: str = "hidden") -> dict:
        """Echo a symbol with defaults only."""
        return {"symbol": symbol, "internal": internal}

    @api.get("/api/v1/demo/multi")
    async def multi_get() -> dict:
        """Read."""
        return {"method": "GET"}

    @api.post("/api/v1/demo/multi")
    async def multi_post() -> dict:
        """Write."""
        return {"method": "POST"}

    @api.get(
        "/api/v1/demo/named",
        openapi_extra={
            "mcp_config": {
                "name": "custom_named",
                "prompts": [
                    {
                        "name": "named_prompt",
                        "description": "Summarize a symbol.",
                        "content": "Summarize {symbol} over {years} years{note}.",
                        "arguments": [
                            {"name": "years", "type": "int", "default": 5},
                            {"name": "note", "type": "str"},
                        ],
                    }
                ],
            }
        },
    )
    async def named(symbol: str) -> dict:
        """A renamed route."""
        return {"symbol": symbol}

    @api.get("/api/v1/other/thing")
    async def thing() -> dict:
        """Another category."""
        return {"results": [{"a": 1}]}

    return api


def _limited_api() -> FastAPI:
    api = FastAPI()

    @api.api_route(
        "/api/v1/demo/limited",
        methods=["GET", "POST"],
        openapi_extra={"mcp_config": {"methods": ["GET"]}},
    )
    async def limited(request: Request) -> dict:
        """Answer GET and POST."""
        return {"method": request.method}

    return api


def _server(api: FastAPI | None = None, **settings):
    return create_mcp_server(
        MCPSettings(
            api_prefix="/api/v1",
            default_skills_dir=None,
            enable_cli_tools=False,
            **settings,
        ),
        api or _api(),
    )


async def _tools(server) -> dict:
    async with Client(server) as client:
        return {tool.name: tool for tool in await client.list_tools()}


class TestAllowedCategories:
    """Restricting the served categories."""

    @pytest.mark.asyncio
    async def test_other_categories_are_not_served(self):
        """Tools outside ``allowed_tool_categories`` are neither listed nor callable."""
        server = _server(allowed_tool_categories=["demo"])
        tools = await _tools(server)
        assert "demo_echo" in tools
        assert "other_thing" not in tools
        async with Client(server) as client:
            with pytest.raises(ToolError, match="Unknown tool"):
                await client.call_tool("other_thing", {})

    @pytest.mark.asyncio
    async def test_discovery_cannot_reach_other_categories(self):
        """With discovery, left-out tools can't be searched or called."""
        server = _server(allowed_tool_categories=["demo"], enable_tool_discovery=True)
        async with Client(server) as client:
            found = await client.call_tool("search_tools", {"query": "category thing"})
            with pytest.raises(ToolError, match="Unknown tool"):
                await client.call_tool(
                    "call_tool", {"name": "other_thing", "arguments": {}}
                )
        assert "other_thing" not in str(found.content)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("allowed", [None, ["all"]])
    async def test_unrestricted(self, allowed):
        """``None`` or ``all`` serves every category."""
        tools = await _tools(_server(allowed_tool_categories=allowed))
        assert {"demo_echo", "other_thing"} <= set(tools)


class TestMethods:
    """Choosing the HTTP methods served as tools."""

    @pytest.mark.asyncio
    @pytest.mark.filterwarnings("ignore:Duplicate Operation ID:UserWarning")
    async def test_configured_methods_only(self):
        """``methods`` leaves the other methods of a route out."""
        server = _server(_limited_api())
        tools = await _tools(server)
        async with Client(server) as client:
            result = await client.call_tool("demo_limited", {})
        assert "demo_limited_post" not in tools
        assert result.structured_content == {"method": "GET"}

    @pytest.mark.asyncio
    async def test_methods_of_one_path_get_distinct_names(self):
        """Every method of a path is its own tool; non-GET methods carry a suffix."""
        server = _server()
        async with Client(server) as client:
            read = await client.call_tool("demo_multi", {})
            write = await client.call_tool("demo_multi_post", {})
        assert read.structured_content == {"method": "GET"}
        assert write.structured_content == {"method": "POST"}


class TestExcludeArgs:
    """Hiding arguments from the tool schema."""

    @pytest.mark.asyncio
    async def test_excluded_argument_is_hidden_and_defaulted(self):
        """An excluded argument leaves the schema and the route's default applies."""
        server = _server()
        tools = await _tools(server)
        async with Client(server) as client:
            result = await client.call_tool("demo_echo", {"symbol": "AAPL"})
        schema = tools["demo_echo"].input_schema
        assert set(schema["properties"]) == {"symbol"}
        assert schema["required"] == ["symbol"]
        assert result.structured_content == {"symbol": "AAPL", "internal": "hidden"}

    @pytest.mark.asyncio
    async def test_schema_with_only_optional_arguments(self):
        """Excluding from a schema of optional arguments leaves nothing required."""
        schema = (await _tools(_server()))["demo_defaults"].input_schema
        assert set(schema["properties"]) == {"symbol"}
        assert schema["required"] == []


class TestRenamedToolPrompts:
    """Inline prompts of a route with a configured tool name."""

    @pytest.mark.asyncio
    async def test_prompt_names_the_renamed_tool(self):
        """The prompt is attached to, and points at, the configured tool name."""
        server = _server()
        tools = await _tools(server)
        async with Client(server) as client:
            prompt = await client.get_prompt(
                "named_prompt", {"symbol": "AAPL", "note": "!"}
            )
        assert "**Associated Prompts:**\n- **named_prompt**" in (
            tools["custom_named"].description or ""
        )
        assert prompt.messages[0].content.text == (
            "Use the tool, custom_named, to perform the following task.\n\n"
            "Summarize AAPL over 5 years!."
        )


class TestInlinePromptArguments:
    """Required and optional arguments of inline prompts."""

    @pytest.mark.asyncio
    async def test_arguments_without_defaults_are_required(self):
        """Endpoint parameters and prompt arguments without a default are required."""
        async with Client(_server()) as client:
            prompts = {prompt.name: prompt for prompt in await client.list_prompts()}
            with pytest.raises(MCPError, match="Missing required arguments"):
                await client.get_prompt("named_prompt", {"note": "!"})
        required = {
            argument.name: argument.required
            for argument in prompts["named_prompt"].arguments or []
        }
        assert required == {"symbol": True, "years": False, "note": True}
