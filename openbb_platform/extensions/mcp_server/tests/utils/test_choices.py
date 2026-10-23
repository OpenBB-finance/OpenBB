"""Tests for ``openbb_mcp_server.utils.choices``."""

from typing import Annotated

import pytest
from fastapi import FastAPI, Query
from fastmcp import Client

from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.utils.choices import expose_choices, schema_values

ONE_PROVIDER = {"type": "string", "const": "cboe"}
TWO_PROVIDERS = {"type": "string", "enum": ["fmp", "intrinio"]}


def _expose(parameter: dict, provider: dict | None = None, tools=None) -> dict:
    properties = {"param": parameter}
    if provider is not None:
        properties["provider"] = provider
    exposed = expose_choices({"type": "object", "properties": properties}, tools or {})
    return exposed["properties"]["param"]


class TestSchemaValues:
    """Reading the enumerated values of a schema."""

    @pytest.mark.parametrize(
        ("schema", "expected"),
        [
            ({"type": "string"}, ([], True)),
            ({"type": "string", "enum": ["a", "b"]}, (["a", "b"], False)),
            ({"const": "x"}, (["x"], False)),
            (
                {"anyOf": [{"type": "string", "enum": ["a"]}, {"type": "null"}]},
                (["a"], False),
            ),
            (
                {"oneOf": [{"type": "string"}, {"type": "string", "enum": ["a"]}]},
                (["a"], True),
            ),
            ({"anyOf": [{"type": "null"}, "junk"]}, ([], False)),
        ],
    )
    def test_values_and_free_branches(self, schema, expected):
        """Enum and const values are collected; unconstrained non-null branches are flagged."""
        assert schema_values(schema) == expected


class TestStaticChoices:
    """Static choices becoming ``enum`` constraints."""

    def test_widget_options_become_enum(self):
        """Top-level widget options constrain the parameter and the widget config is dropped."""
        exposed = _expose(
            {
                "type": "string",
                "title": "Strategy",
                "default": "buy_call",
                "x-widget_config": {
                    "options": [
                        {"label": "Buy Call", "value": "buy_call"},
                        {"label": "Sell Call", "value": "sell_call"},
                        "buy_call",
                    ]
                },
            }
        )
        assert exposed == {
            "type": "string",
            "title": "Strategy",
            "default": "buy_call",
            "enum": ["buy_call", "sell_call"],
        }

    def test_top_level_choices_become_enum_and_stay_nullable(self):
        """``choices`` constrain a nullable parameter without losing the null branch."""
        exposed = _expose(
            {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "title": "Kind",
                "choices": ["a", "b"],
            }
        )
        assert exposed == {
            "title": "Kind",
            "anyOf": [{"type": "string", "enum": ["a", "b"]}, {"type": "null"}],
        }

    def test_provider_choices_replace_a_free_branch(self):
        """Provider choices override a merged free-text branch when the provider is the tool's only one."""
        exposed = _expose(
            {
                "anyOf": [{"type": "string"}, {"type": "string", "enum": ["us", "eu"]}],
                "title": "cboe",
                "default": "us",
                "cboe": {"choices": ["us", "eu", "au"]},
            },
            ONE_PROVIDER,
        )
        assert exposed == {
            "title": "cboe",
            "default": "us",
            "type": "string",
            "enum": ["us", "eu", "au"],
        }

    @pytest.mark.parametrize(
        ("options", "expected_type"),
        [
            ([1, 5, 10], "integer"),
            ([1, 2.5], "number"),
            ([True, False], "boolean"),
            (["a", 1], None),
            ([["a", "b"]], None),
        ],
    )
    def test_enum_type_follows_the_values(self, options, expected_type):
        """The enum's JSON type is the one its values share, if any."""
        exposed = _expose(
            {
                "type": "string",
                "cboe": {"x-widget_config": {"options": options}},
            },
            ONE_PROVIDER,
        )
        assert exposed.get("type") == expected_type
        assert exposed["enum"] == options

    def test_complete_enum_is_kept(self):
        """An already constrained schema keeps its enum; only the extras go."""
        exposed = _expose(
            {
                "type": "string",
                "enum": ["1m", "1d"],
                "title": "cboe",
                "cboe": {"multiple_items_allowed": False, "choices": ["1m", "1d"]},
            },
            ONE_PROVIDER,
        )
        assert exposed == {"type": "string", "enum": ["1m", "1d"], "title": "cboe"}

    def test_differing_provider_choices_are_listed_per_provider(self):
        """A parameter shared by providers with different choices gets a union enum and a per-provider note."""
        exposed = _expose(
            {
                "anyOf": [
                    {"type": "string", "enum": ["1d", "1W"]},
                    {"type": "string", "enum": ["1d", "1M"]},
                ],
                "title": "fmp,intrinio",
                "description": "Interval.",
                "fmp": {"choices": ["1d", "1W"]},
                "intrinio": {"choices": ["1d", "1M"]},
            },
            TWO_PROVIDERS,
        )
        assert exposed["anyOf"] == [
            {"type": "string", "enum": ["1d", "1W"]},
            {"type": "string", "enum": ["1d", "1M"]},
        ]
        assert exposed["description"] == (
            "Interval. Valid values by provider: fmp: 1d, 1W; intrinio: 1d, 1M."
        )

    def test_provider_specific_parameter_uses_its_title_providers(self):
        """A parameter titled with one provider of a multi-provider tool is fully covered by that provider."""
        exposed = _expose(
            {"type": "string", "title": "fmp", "fmp": {"choices": ["a", "b"]}},
            TWO_PROVIDERS,
        )
        assert exposed == {"type": "string", "title": "fmp", "enum": ["a", "b"]}

    def test_choices_of_some_providers_are_described(self):
        """Choices that only some of the parameter's providers declare are described, not enforced."""
        exposed = _expose(
            {"type": "string", "title": "Symbol", "fmp": {"choices": ["a", "b"]}},
            TWO_PROVIDERS,
        )
        assert exposed == {
            "type": "string",
            "title": "Symbol",
            "description": "Valid values for provider fmp: a, b.",
        }

    def test_choices_without_a_provider_parameter(self):
        """Without a provider parameter the declared providers are the parameter's providers."""
        exposed = _expose({"type": "string", "custom": {"choices": ["x", "y"]}})
        assert exposed == {"type": "string", "enum": ["x", "y"]}


class TestMultipleItems:
    """Choices of comma-separated, multi-valued parameters."""

    def test_provider_multi_choices_are_described(self):
        """Multi-valued provider choices are listed in the description."""
        exposed = _expose(
            {
                "type": "string",
                "title": "oecd",
                "description": "The country.",
                "oecd": {"multiple_items_allowed": True, "choices": ["japan", "all"]},
            },
            {"type": "string", "const": "oecd"},
        )
        assert exposed == {
            "type": "string",
            "title": "oecd",
            "description": "The country. Valid values for provider oecd (comma-separate several): japan, all.",
        }

    def test_multi_select_widget_options_are_described(self):
        """Multi-select widget options are listed in the description."""
        exposed = _expose(
            {
                "type": "string",
                "x-widget_config": {"multiSelect": True, "options": ["a", "b"]},
            }
        )
        assert exposed == {
            "type": "string",
            "description": "Valid values (comma-separate several): a, b.",
        }

    def test_multi_flag_without_choices_is_dropped(self):
        """A multi-item flag with no choices leaves only the core description."""
        exposed = _expose(
            {
                "type": "string",
                "description": "Symbols.",
                "fmp": {"multiple_items_allowed": True},
            },
            TWO_PROVIDERS,
        )
        assert exposed == {"type": "string", "description": "Symbols."}


class TestDynamicChoices:
    """Choices listed by another tool."""

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/v1/demo/tickers",
            "api/v1/demo/tickers",
            "http://127.0.0.1:8000/api/v1/demo/tickers?x=1",
        ],
    )
    def test_options_endpoint_points_to_its_tool(self, endpoint):
        """An options endpoint names the tool that lists the values and how to call it."""
        exposed = _expose(
            {
                "type": "number",
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": endpoint,
                    "optionsParams": {"strike_list": True, "symbol": "$symbol"},
                },
            },
            tools={"/api/v1/demo/tickers": "demo_tickers"},
        )
        assert exposed == {
            "type": "number",
            "description": "Get the valid values from the `demo_tickers` tool with strike_list=true, symbol=<the symbol you pass here>.",
        }

    def test_provider_options_endpoint_is_attributed(self):
        """A provider's options endpoint note names the provider."""
        exposed = _expose(
            {
                "type": "string",
                "description": "Symbol.",
                "cboe": {
                    "x-widget_config": {"optionsEndpoint": "/api/v1/cboe/symbols"},
                },
            },
            ONE_PROVIDER,
            tools={"/api/v1/cboe/symbols": "cboe_symbols"},
        )
        assert exposed == {
            "type": "string",
            "description": "Symbol. For provider cboe: Get the valid values from the `cboe_symbols` tool.",
        }

    def test_options_endpoint_that_is_not_a_tool_is_skipped(self):
        """An endpoint that is not an MCP tool adds nothing."""
        exposed = _expose(
            {
                "type": "string",
                "x-widget_config": {"optionsEndpoint": "/api/v1/hidden"},
            }
        )
        assert exposed == {"type": "string"}


class TestSchemaShapes:
    """Inputs that carry no choices."""

    def test_schema_without_properties(self):
        """A schema without properties is returned unchanged."""
        schema = {"type": "object"}
        assert expose_choices(schema, {}) is schema

    def test_non_dict_properties_pass_through(self):
        """Boolean property schemas are left alone."""
        exposed = expose_choices({"type": "object", "properties": {"any": True}}, {})
        assert exposed == {"type": "object", "properties": {"any": True}}

    def test_dict_values_that_are_not_extras_are_kept(self):
        """A dict default is part of the schema, not a provider extra."""
        schema = {"type": "object", "default": {"window": 5}}
        assert _expose(schema) == schema

    def test_schema_keywords_are_not_mistaken_for_extras(self):
        """A nested object with a ``choices`` property keeps its schema."""
        schema = {
            "type": "object",
            "properties": {"choices": {"type": "array"}, "name": {"type": "string"}},
        }
        assert _expose(schema) == schema


class TestServerChoices:
    """Choices exposed on the tools of a served FastAPI app."""

    @pytest.mark.asyncio
    async def test_choices_reach_the_tool_schemas(self):
        """Static options become an enum and options endpoints point at their tools."""
        api = FastAPI()

        @api.get("/api/v1/demo/strikes")
        async def strikes(symbol: str = "SPY") -> list[float]:
            """List strikes."""
            return [1.0, 2.0]

        @api.get("/api/v1/demo/payoff")
        async def payoff(
            strategy: Annotated[
                str,
                Query(
                    json_schema_extra={
                        "x-widget_config": {
                            "options": [
                                {"label": "Buy", "value": "buy"},
                                {"label": "Sell", "value": "sell"},
                            ]
                        }
                    }
                ),
            ] = "buy",
            strike: Annotated[
                float | None,
                Query(
                    description="The strike.",
                    json_schema_extra={
                        "x-widget_config": {
                            "type": "endpoint",
                            "optionsEndpoint": "/api/v1/demo/strikes",
                            "optionsParams": {"symbol": "$symbol"},
                        }
                    },
                ),
            ] = None,
        ) -> dict:
            """Draw a payoff."""
            return {"strategy": strategy, "strike": strike}

        server = create_mcp_server(
            MCPSettings(
                api_prefix="/api/v1", default_skills_dir=None, enable_cli_tools=False
            ),
            api,
        )
        async with Client(server) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}
        properties = tools["demo_payoff"].input_schema["properties"]
        assert properties["strategy"]["enum"] == ["buy", "sell"]
        assert "x-widget_config" not in properties["strategy"]
        assert properties["strike"]["description"] == (
            "The strike. Get the valid values from the `demo_strikes` tool with symbol=<the symbol you pass here>."
        )
