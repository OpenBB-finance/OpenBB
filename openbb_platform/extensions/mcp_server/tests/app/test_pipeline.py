"""Tests for ``openbb_mcp_server.app.pipeline``."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastmcp import Client
from fastmcp.exceptions import ToolError
from openbb_core.api.rest_api import app as rest_app
from pydantic import BaseModel

from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings


class ScaleBody(BaseModel):
    """Request body of the scale route."""

    data: list[dict]
    factor: float = 2.0


class KeysBody(BaseModel):
    """Request body of the keys route."""

    payload: dict


def _api(calls: list[str]) -> FastAPI:
    api = FastAPI()

    @api.get("/api/v1/prices/history")
    async def history(symbol: str = "AAPL", rows: int = 3) -> dict:
        """Return a price history."""
        calls.append("history")
        return {
            "results": [{"symbol": symbol, "close": float(i)} for i in range(rows)],
            "provider": "test",
        }

    @api.post("/api/v1/calc/scale")
    async def scale(body: ScaleBody) -> dict:
        """Scale every close."""
        calls.append("scale")
        return {
            "results": [
                {**row, "close": row["close"] * body.factor} for row in body.data
            ]
        }

    @api.get("/api/v1/calc/listing")
    async def listing() -> list[dict]:
        """Return bare rows."""
        return [{"close": 5.0}]

    @api.get("/api/v1/calc/text", response_class=PlainTextResponse)
    async def text() -> str:
        """Return plain text."""
        return "plain words"

    @api.get("/api/v1/calc/summary")
    async def summary() -> dict:
        """Return a summary without a ``results`` field."""
        return {"count": 2, "mean": 1.5}

    @api.post("/api/v1/calc/keys")
    async def keys(body: KeysBody) -> dict:
        """Return the sorted keys of a payload."""
        return {"results": sorted(body.payload)}

    @api.get("/api/v1/calc/shout")
    async def shout(text: str) -> dict:
        """Upper-case a text."""
        return {"results": text.upper()}

    @api.get("/api/v1/calc/figure")
    async def figure() -> dict:
        """Return a Plotly figure."""
        return {
            "data": [
                {"type": "scatter", "name": "close", "x": ["d1", "d2"], "y": [1.0, 2.0]}
            ],
            "layout": {},
        }

    @api.get("/api/v1/calc/fail")
    async def fail() -> dict:
        """Fail."""
        raise HTTPException(status_code=400, detail="boom")

    return api


def _server(calls: list[str], *, discovery: bool = False):
    settings = MCPSettings(
        api_prefix="/api/v1",
        enable_tool_discovery=discovery,
        default_skills_dir=None,
        enable_cli_tools=False,
    )
    return create_mcp_server(settings, _api(calls))


async def _run(server, **arguments):
    async with Client(server) as client:
        result = await client.call_tool("run_pipeline", arguments)
    return result.structured_content


PRICES_TO_SCALE = [
    {"id": "prices", "tool": "prices_history", "arguments": {"rows": 3}},
    {
        "id": "scaled",
        "tool": "calc_scale",
        "arguments": {"factor": 10},
        "inputs": {"data": "prices"},
    },
]
SCALED = {
    "results": [
        {"symbol": "AAPL", "close": 0.0},
        {"symbol": "AAPL", "close": 10.0},
        {"symbol": "AAPL", "close": 20.0},
    ]
}


class TestRunPipeline:
    """Chaining tools on the server."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("discovery", [False, True])
    async def test_feeds_results_into_later_steps(self, discovery):
        """An earlier step's ``results`` fill a later step's argument; the last step is returned."""
        calls: list[str] = []
        out = await _run(_server(calls, discovery=discovery), steps=PRICES_TO_SCALE)
        assert out == {"scaled": SCALED}
        assert calls == ["history", "scale"]

    @pytest.mark.asyncio
    async def test_returns_selected_outputs(self):
        """``outputs`` selects which step outputs come back."""
        out = await _run(
            _server([]), steps=PRICES_TO_SCALE, outputs=["prices", "scaled"]
        )
        assert out["prices"]["provider"] == "test"
        assert out["scaled"] == SCALED

    @pytest.mark.asyncio
    async def test_steps_without_ids_are_keyed_by_position(self):
        """A step without an ``id`` is referenced and returned by its position."""
        steps = [
            {"tool": "prices_history", "arguments": {"rows": 1}},
            {"tool": "calc_scale", "inputs": {"data": "0"}},
        ]
        out = await _run(_server([]), steps=steps)
        assert out == {"1": {"results": [{"symbol": "AAPL", "close": 0.0}]}}

    @pytest.mark.asyncio
    async def test_unwraps_wrapped_results(self):
        """A tool whose output is wrapped as ``{"result": ...}`` passes the inner value."""
        steps = [
            {"id": "rows", "tool": "calc_listing"},
            {"tool": "calc_scale", "inputs": {"data": "rows"}},
        ]
        out = await _run(_server([]), steps=steps)
        assert out == {"1": {"results": [{"close": 10.0}]}}

    @pytest.mark.asyncio
    async def test_feeds_artifact_rows(self):
        """A chart artifact passes its rows to a later step."""
        steps = [
            {"id": "chart", "tool": "calc_figure"},
            {"id": "scaled", "tool": "calc_scale", "inputs": {"data": "chart"}},
        ]
        out = await _run(_server([]), steps=steps, outputs=["chart", "scaled"])
        assert out["chart"]["type"] == "chart"
        assert out["scaled"] == {
            "results": [{"x": "d1", "close": 2.0}, {"x": "d2", "close": 4.0}]
        }

    @pytest.mark.asyncio
    async def test_passes_other_outputs_whole(self):
        """Outputs without ``results`` or a lone ``result`` are passed unchanged."""
        steps = [
            {"id": "summary", "tool": "calc_summary"},
            {"id": "keys", "tool": "calc_keys", "inputs": {"payload": "summary"}},
            {"id": "text", "tool": "calc_text"},
            {"id": "shout", "tool": "calc_shout", "inputs": {"text": "text"}},
        ]
        out = await _run(_server([]), steps=steps, outputs=["keys", "shout"])
        assert out == {
            "keys": {"results": ["count", "mean"]},
            "shout": {"results": "PLAIN WORDS"},
        }

    @pytest.mark.asyncio
    async def test_text_outputs(self):
        """Text output is parsed as JSON when possible and returned verbatim otherwise."""
        server = _server([])

        @server.tool(output_schema=None)
        def raw_json() -> str:
            """Return JSON as text."""
            return '{"results": [{"close": 1.5}]}'

        steps = [
            {"id": "raw", "tool": "raw_json"},
            {"id": "scaled", "tool": "calc_scale", "inputs": {"data": "raw"}},
            {"id": "text", "tool": "calc_text"},
        ]
        out = await _run(server, steps=steps, outputs=["raw", "scaled", "text"])
        assert out == {
            "raw": {"results": [{"close": 1.5}]},
            "scaled": {"results": [{"close": 3.0}]},
            "text": "plain words",
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("arguments", "message"),
        [
            (
                {"steps": [{"id": "a", "tool": "calc_text"}] * 2},
                "Step ids must be unique",
            ),
            (
                {"steps": [{"tool": "run_pipeline"}]},
                "Step '0' cannot call run_pipeline",
            ),
            (
                {
                    "steps": [
                        {"id": "first", "tool": "prices_history"},
                        {"tool": "calc_scale", "inputs": {"data": "later"}},
                        {"id": "later", "tool": "prices_history"},
                    ]
                },
                "Step '1' input 'data' refers to 'later', which is not an earlier step",
            ),
            (
                {"steps": [{"tool": "prices_history"}], "outputs": ["nope"]},
                "Unknown output steps: nope",
            ),
        ],
    )
    async def test_invalid_pipelines_fail_before_running(self, arguments, message):
        """Malformed pipelines are rejected before any step runs."""
        calls: list[str] = []
        with pytest.raises(ToolError, match=message):
            await _run(_server(calls), **arguments)
        assert calls == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tool", "message"),
        [
            ("calc_fail", "Step 'x' \\(calc_fail\\) failed: .*boom"),
            ("missing_tool", "Step 'x' \\(missing_tool\\) failed: Unknown tool"),
        ],
    )
    async def test_step_failures_name_the_step(self, tool, message):
        """A failing or unknown tool reports which step failed."""
        with pytest.raises(ToolError, match=message):
            await _run(_server([]), steps=[{"id": "x", "tool": tool}])


class TestPipelineWithOpenBBCommands:
    """Chaining real OpenBB commands, including one that takes ``data: list[Data]``."""

    @pytest.mark.asyncio
    async def test_command_results_feed_a_data_command(self):
        """``echo`` rows feed the ``scale`` command's ``data`` without leaving the server."""
        server = create_mcp_server(
            MCPSettings(default_skills_dir=None, enable_cli_tools=False), rest_app
        )
        steps = [
            {"id": "rows", "tool": "mcp_fixture_echo", "arguments": {"rows": 3}},
            {
                "tool": "mcp_fixture_scale",
                "arguments": {"factor": 10},
                "inputs": {"data": "rows"},
            },
        ]
        out = await _run(server, steps=steps)
        assert out["1"]["results"] == [
            {"symbol": "AAPL", "value": 0.0},
            {"symbol": "AAPL", "value": 10.0},
            {"symbol": "AAPL", "value": 20.0},
        ]

    @pytest.mark.asyncio
    async def test_data_parameter_schema_is_trimmed(self):
        """The ``Data`` model docstring is reduced to its summary in tool schemas."""
        server = create_mcp_server(
            MCPSettings(default_skills_dir=None, enable_cli_tools=False), rest_app
        )
        async with Client(server) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}
        data = tools["mcp_fixture_scale"].input_schema["properties"]["data"]
        assert data["items"]["description"] == "The OpenBB Standardized Data Model."
        assert data["description"] == "Rows carrying a numeric ``index`` column."
