"""Test schema compression in fastmcp."""

import json
import sys

import pytest
from openbb_core.api.rest_api import app as fastapi_app
from openbb_mcp_server.main import MCPSettings, create_mcp_server

# Skip all tests if Python version < 3.10
if sys.version_info < (3, 10):
    pytest.skip("MCP server requires Python 3.10+", allow_module_level=True)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_schema_compression():
    """Integration test to verify schema compression effectiveness.

    This test verifies that the schema compression in fastmcp is working properly
    and that schemas don't grow to unmanageable sizes.
    """

    settings = MCPSettings(
        name="TestMCP",
        describe_responses=False,
        default_tool_categories=["all"],
        allowed_tool_categories=["news"],  # Limit to news tools (runs faster)
        enable_tool_discovery=True,
    )

    # Create MCP server
    mcp = create_mcp_server(settings, fastapi_app)

    tools = await mcp.get_tools()

    assert len(tools) > 0, "No tools found in MCP server"

    # Check news tools
    for name, tool in list(tools.items()):
        input_schema = tool.parameters
        input_defs = len(input_schema.get("$defs", {}))
        input_chars = len(json.dumps(input_schema))

        # Assert with reasonable sizes
        assert (
            input_chars < 10000
        ), f"Input schema for {name} too large: {input_chars} chars"
        assert input_defs < 10, f"Too many defs in input for {name}: {input_defs}"

        # Output schema if exists
        if hasattr(tool, "output_schema") and tool.output_schema:
            output_schema = tool.output_schema
            output_defs = len(output_schema.get("$defs", {}))
            output_chars = len(json.dumps(output_schema))

            assert (
                output_chars < 20000
            ), f"Output schema for {name} too large: {output_chars} chars"
            assert (
                output_defs < 20
            ), f"Too many defs in output for {name}: {output_defs}"
