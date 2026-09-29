"""Tests for ``openbb_mcp_server.app.artifacts``."""

import base64
import json
import struct

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastmcp import Client
from pydantic import BaseModel

from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.app.artifacts import (
    ARTIFACT_SCHEMA,
    _decode,
    artifact_output_schema,
    convert_figures,
    figure_to_artifact,
    is_artifact,
    is_plotly_figure,
)
from openbb_mcp_server.models.settings import MCPSettings

_CODES = {"f8": "d", "i4": "i", "i1": "b", "u8": "Q"}


def _typed(values: list, dtype: str = "f8", shape: str | None = None) -> dict:
    raw = struct.pack(f"<{len(values)}{_CODES[dtype]}", *values)
    array = {"dtype": dtype, "bdata": base64.b64encode(raw).decode()}
    if shape:
        array["shape"] = shape
    return array


def _figure(*traces: dict, **layout) -> dict:
    return {"data": list(traces), "layout": layout}


def _artifact(figure: dict) -> dict:
    return figure_to_artifact(figure, "fallback_name", "A description.")


class TestDecode:
    """Decoding Plotly data arrays."""

    @pytest.mark.parametrize(
        ("values", "expected"),
        [
            ([1, 2], [1, 2]),
            (_typed([1.5, 2.25]), [1.5, 2.25]),
            (_typed([-1, 2], "i1"), [-1, 2]),
            (_typed([3, 4], "i4"), [3, 4]),
            (_typed([7], "u8"), [7]),
            ({"bdata": base64.b64encode(struct.pack("<d", 0.5)).decode()}, [0.5]),
            (_typed([1.0, 2.0, 3.0, 4.0], shape="2, 2"), [[1.0, 2.0], [3.0, 4.0]]),
            ({"dtype": "c16", "bdata": "AAAA"}, []),
            ({"dtype": "f8"}, []),
            (None, []),
        ],
    )
    def test_decode(self, values, expected):
        """Lists pass through, typed arrays decode, and anything else is empty."""
        assert _decode(values) == expected


class TestRecognition:
    """Recognizing figures and artifacts."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (_figure({"type": "scatter"}), True),
            ({"data": [{"type": "scatter"}]}, False),
            (_figure({"x": [1]}), False),
            ({"data": "rows", "layout": {}}, False),
            ([], False),
        ],
    )
    def test_is_plotly_figure(self, value, expected):
        """A figure has a layout and typed traces."""
        assert is_plotly_figure(value) is expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ({"type": "chart", "content": [], "uuid": "u"}, True),
            ({"type": "table", "content": [], "uuid": "u"}, True),
            ({"type": "text", "content": [], "uuid": "u"}, False),
            ({"type": "chart", "content": "x", "uuid": "u"}, False),
            ({"type": "chart", "content": []}, False),
            ("chart", False),
        ],
    )
    def test_is_artifact(self, value, expected):
        """An artifact is a typed dict with row content and a uuid."""
        assert is_artifact(value) is expected


class TestChartArtifacts:
    """Figures Copilot can draw natively."""

    def test_line_chart_merges_series_on_x(self):
        """Line traces sharing an x axis become one row per x value."""
        artifact = _artifact(
            _figure(
                {
                    "type": "scatter",
                    "mode": "lines",
                    "name": "Calls",
                    "x": ["2026-01-02", "2026-02-20"],
                    "y": _typed([1.5, 2.25]),
                },
                {
                    "type": "scatter",
                    "name": "Puts",
                    "x": ["2026-02-20"],
                    "y": [3.0],
                },
                title={"text": "Term Structure"},
                xaxis={"title": {"text": "Expiration"}},
            )
        )
        assert artifact["type"] == "chart"
        assert artifact["name"] == "Term Structure"
        assert artifact["description"] == "A description."
        assert artifact["chart_params"] == {
            "chartType": "line",
            "xKey": "Expiration",
            "yKey": ["Calls", "Puts"],
        }
        assert artifact["content"] == [
            {"Expiration": "2026-01-02", "Calls": 1.5},
            {"Expiration": "2026-02-20", "Calls": 2.25, "Puts": 3.0},
        ]
        assert is_artifact(artifact)

    @pytest.mark.parametrize(
        ("traces", "chart_type"),
        [
            ([{"type": "bar", "x": ["a"], "y": [1]}], "bar"),
            (
                [{"type": "scatter", "mode": "markers", "x": [1, 2], "y": [3, 4]}],
                "scatter",
            ),
            ([{"type": "scattergl", "mode": "markers", "x": ["a"], "y": [1]}], "line"),
            ([{"type": "scatter", "mode": "markers", "x": [True], "y": [1]}], "line"),
            (
                [
                    {"type": "bar", "x": ["a"], "y": [1]},
                    {"type": "scatter", "mode": "markers", "x": ["a"], "y": [2]},
                ],
                "line",
            ),
        ],
    )
    def test_chart_type(self, traces, chart_type):
        """Bars draw as bar, numeric marker plots as scatter, everything else as line."""
        assert _artifact(_figure(*traces))["chart_params"]["chartType"] == chart_type

    def test_horizontal_bars_use_the_y_axis_as_categories(self):
        """Horizontal bars take categories from y and values from x."""
        artifact = _artifact(
            _figure(
                {
                    "type": "bar",
                    "orientation": "h",
                    "name": "Weight",
                    "y": ["AAPL"],
                    "x": [0.4],
                },
                yaxis={"title": "Symbol"},
            )
        )
        assert artifact["chart_params"] == {
            "chartType": "bar",
            "xKey": "Symbol",
            "yKey": ["Weight"],
        }
        assert artifact["content"] == [{"Symbol": "AAPL", "Weight": 0.4}]

    def test_series_names_are_unique_and_never_the_x_key(self):
        """Unnamed, duplicate, and x-colliding series names get distinct column names."""
        artifact = _artifact(
            _figure(
                {"type": "scatter", "x": [1], "y": [1]},
                {"type": "scatter", "name": "a", "x": [1], "y": [2]},
                {"type": "scatter", "name": "a", "x": [1], "y": [3]},
                {"type": "scatter", "name": "x", "x": [1], "y": [4]},
            )
        )
        assert artifact["chart_params"]["yKey"] == ["series 1", "a", "a (2)", "x (2)"]
        assert artifact["content"] == [
            {"x": 1, "series 1": 1, "a": 2, "a (2)": 3, "x (2)": 4}
        ]

    def test_missing_x_uses_positions(self):
        """A trace with only y values is indexed by position."""
        artifact = _artifact(_figure({"type": "bar", "y": [5, 6]}))
        assert artifact["content"] == [
            {"x": 0, "series 1": 5},
            {"x": 1, "series 1": 6},
        ]

    def test_multicategory_x_values(self):
        """List-valued categories keep their value as a row key."""
        artifact = _artifact(_figure({"type": "bar", "x": [["2026", "Q1"]], "y": [1]}))
        assert artifact["content"] == [{"x": ["2026", "Q1"], "series 1": 1}]

    @pytest.mark.parametrize(
        ("hole", "chart_type"), [(None, "pie"), (0, "pie"), (0.4, "donut")]
    )
    def test_pie_and_donut(self, hole, chart_type):
        """A single pie trace becomes a pie or, with a hole, a donut."""
        trace = {
            "type": "pie",
            "labels": ["Stocks", "Bonds"],
            "values": _typed([60, 40], "i4"),
        }
        if hole is not None:
            trace["hole"] = hole
        artifact = _artifact(_figure(trace, title="Allocation"))
        assert artifact["name"] == "Allocation"
        assert artifact["chart_params"] == {
            "chartType": chart_type,
            "angleKey": "value",
            "calloutLabelKey": "label",
        }
        assert artifact["content"] == [
            {"label": "Stocks", "value": 60},
            {"label": "Bonds", "value": 40},
        ]


class TestTableArtifacts:
    """Figures Copilot cannot draw become tables of their data."""

    def test_surface_rows(self):
        """A surface lists every z value with its x and y, or its position where they are missing."""
        artifact = _artifact(
            _figure(
                {
                    "type": "surface",
                    "name": "IV",
                    "x": [100],
                    "y": [30],
                    "z": _typed([0.2, 0.25, 0.3, 0.35], shape="2, 2"),
                }
            )
        )
        assert artifact["type"] == "table"
        assert artifact["name"] == "fallback_name"
        assert "chart_params" not in artifact
        assert artifact["content"] == [
            {"series": "IV", "trace_type": "surface", "x": 100, "y": 30, "z": 0.2},
            {"series": "IV", "trace_type": "surface", "x": 1, "y": 30, "z": 0.25},
            {"series": "IV", "trace_type": "surface", "x": 100, "y": 1, "z": 0.3},
            {"series": "IV", "trace_type": "surface", "x": 1, "y": 1, "z": 0.35},
        ]

    def test_candlestick_rows(self):
        """Candlesticks list their open, high, low, and close per x."""
        artifact = _artifact(
            _figure(
                {
                    "type": "candlestick",
                    "x": ["d1", "d2"],
                    "open": [1, 2],
                    "high": [3, 4],
                    "low": [0, 1],
                    "close": [2],
                }
            )
        )
        assert artifact["content"] == [
            {
                "series": "series 1",
                "trace_type": "candlestick",
                "x": "d1",
                "open": 1,
                "high": 3,
                "low": 0,
                "close": 2,
            },
            {
                "series": "series 1",
                "trace_type": "candlestick",
                "x": "d2",
                "open": 2,
                "high": 4,
                "low": 1,
            },
        ]

    def test_mixed_traces_rows(self):
        """Pies among other traces list labels and values; other traces list their points."""
        artifact = _artifact(
            _figure(
                {"type": "pie", "name": "Mix", "labels": ["a"], "values": [1]},
                {"type": "histogram", "name": "Hist", "x": [1, 2], "y": [5]},
            )
        )
        assert artifact["type"] == "table"
        assert artifact["content"] == [
            {"series": "Mix", "trace_type": "pie", "label": "a", "value": 1},
            {"series": "Hist", "trace_type": "histogram", "x": 1, "y": 5},
            {"series": "Hist", "trace_type": "histogram", "x": 2},
        ]

    def test_mixed_orientation_is_a_table(self):
        """Traces on different category axes cannot share rows and become a table."""
        artifact = _artifact(
            _figure(
                {"type": "bar", "x": ["a"], "y": [1]},
                {"type": "bar", "orientation": "h", "y": ["b"], "x": [2]},
            )
        )
        assert artifact["type"] == "table"

    def test_empty_figure(self):
        """A figure without traces is an empty table."""
        artifact = _artifact(_figure())
        assert (artifact["type"], artifact["content"]) == ("table", [])


class TestConvertFigures:
    """Replacing figures inside tool payloads."""

    def test_figure_payload(self):
        """A bare figure becomes an artifact."""
        artifact = convert_figures(
            _figure({"type": "bar", "x": ["a"], "y": [1]}), "demo"
        )
        assert artifact["type"] == "chart"
        assert artifact["name"] == "demo"
        assert artifact["description"] == "Output of the demo tool."

    def test_obbject_chart(self):
        """An OBBject's Plotly chart is replaced by an artifact; the results stay."""
        payload = {
            "results": [{"close": 1}],
            "chart": {
                "content": _figure({"type": "bar", "x": ["a"], "y": [1]}),
                "format": "plotly",
            },
        }
        converted = convert_figures(payload, "demo")
        assert converted["results"] == [{"close": 1}]
        assert converted["chart"]["type"] == "chart"

    def test_dispatcher_result_chart(self):
        """A figure nested in a dispatcher ``result`` is converted in place."""
        payload = {
            "ok": True,
            "result": {
                "chart": {"content": _figure({"type": "bar", "x": [1], "y": [1]})}
            },
        }
        converted = convert_figures(payload, "openbb_dispatch")
        assert converted["ok"] is True
        assert converted["result"]["chart"]["type"] == "chart"

    @pytest.mark.parametrize(
        "payload",
        [
            {"results": [], "chart": {"content": None}},
            {"results": [], "chart": None},
            {"ok": True, "result": {"results": []}},
            {"result": [1, 2]},
            [1, 2],
            None,
        ],
    )
    def test_payloads_without_figures_are_unchanged(self, payload):
        """Payloads without a figure are returned as they are."""
        assert convert_figures(payload, "demo") is payload


class TestArtifactOutputSchema:
    """Output schemas of tools whose OBBject may carry a chart."""

    def test_chart_property_becomes_an_artifact(self):
        """The ``chart`` property is replaced by a nullable artifact."""
        schema = {
            "type": "object",
            "properties": {"results": {}, "chart": {"type": "object"}},
        }
        assert artifact_output_schema(schema) == {
            "type": "object",
            "properties": {
                "results": {},
                "chart": {"anyOf": [ARTIFACT_SCHEMA, {"type": "null"}]},
            },
        }

    @pytest.mark.parametrize(
        "schema",
        [
            None,
            {},
            {"type": "object"},
            {"type": "object", "properties": {"results": {}}},
        ],
    )
    def test_other_schemas_are_unchanged(self, schema):
        """Schemas without a ``chart`` property are returned as they are."""
        assert artifact_output_schema(schema) is schema


class ChartedOutput(BaseModel):
    """An OBBject-like response."""

    results: list[dict]
    chart: dict | None = None


FIGURE = _figure(
    {
        "type": "scatter",
        "name": "close",
        "x": ["2026-01-02", "2026-01-05"],
        "y": _typed([1.0, 2.0]),
    },
    title="Prices",
)


def _chart_server():
    api = FastAPI()

    @api.get("/api/v1/demo/figure")
    async def figure() -> dict:
        """Return a figure."""
        return FIGURE

    @api.get("/api/v1/demo/untyped", response_class=JSONResponse)
    async def untyped():
        """Return a figure without a response schema."""
        return JSONResponse(FIGURE)

    @api.get("/api/v1/demo/charted")
    async def charted(chart: bool = False) -> ChartedOutput:
        """Return results with an optional chart."""
        return ChartedOutput(
            results=[{"close": 1.0}],
            chart={"content": FIGURE, "format": "plotly"} if chart else None,
        )

    @api.get("/api/v1/demo/rows")
    async def rows() -> dict:
        """Return plain rows."""
        return {"results": [{"close": 1.0}]}

    @api.get("/api/v1/demo/text", response_class=PlainTextResponse)
    async def text() -> str:
        """Return text."""
        return "plain words"

    return create_mcp_server(
        MCPSettings(
            api_prefix="/api/v1", default_skills_dir=None, enable_cli_tools=False
        ),
        api,
    )


class TestChartArtifactMiddleware:
    """Tool results served through the middleware."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool", ["demo_figure", "demo_untyped"])
    async def test_figure_results_become_artifacts(self, tool):
        """A figure result is returned as an artifact in both structured and text content."""
        async with Client(_chart_server()) as client:
            result = await client.call_tool(tool, {})
        artifact = result.structured_content
        assert artifact["type"] == "chart"
        assert artifact["name"] == "Prices"
        assert artifact["content"] == [
            {"x": "2026-01-02", "close": 1.0},
            {"x": "2026-01-05", "close": 2.0},
        ]
        assert json.loads(result.content[0].text) == artifact

    @pytest.mark.asyncio
    async def test_obbject_chart_matches_the_output_schema(self):
        """An OBBject chart becomes an artifact that validates against the tool's output schema."""
        async with Client(_chart_server()) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}
            result = await client.call_tool("demo_charted", {"chart": True})
            plain = await client.call_tool("demo_charted", {})
        chart_schema = tools["demo_charted"].output_schema["properties"]["chart"]
        assert chart_schema == {"anyOf": [ARTIFACT_SCHEMA, {"type": "null"}]}
        assert result.structured_content["results"] == [{"close": 1.0}]
        assert result.structured_content["chart"]["type"] == "chart"
        assert plain.structured_content == {"results": [{"close": 1.0}], "chart": None}

    @pytest.mark.asyncio
    async def test_other_results_are_unchanged(self):
        """Rows and plain text pass through untouched, and a text tool declares no output schema."""
        async with Client(_chart_server()) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}
            rows = await client.call_tool("demo_rows", {})
            text = await client.call_tool("demo_text", {})
        assert tools["demo_text"].output_schema is None
        assert rows.structured_content == {"results": [{"close": 1.0}]}
        assert text.content[0].text == "plain words"
