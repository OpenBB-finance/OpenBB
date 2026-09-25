"""Turn Plotly figures in tool results into OpenBB Workspace artifacts."""

from __future__ import annotations

import base64
import json
import struct
import uuid
from typing import TYPE_CHECKING, Any

from fastmcp.server.middleware import Middleware
from fastmcp.tools.base import ToolResult
from mcp.types import TextContent

if TYPE_CHECKING:
    import mcp.types as mt
    from fastmcp.server.middleware import CallNext, MiddlewareContext

_TYPED_ARRAY_FORMATS = {
    "i1": "b",
    "u1": "B",
    "i2": "h",
    "u2": "H",
    "i4": "i",
    "u4": "I",
    "i8": "q",
    "u8": "Q",
    "f4": "f",
    "f8": "d",
    "b1": "?",
}
_XY_TRACE_TYPES = frozenset({"scatter", "scattergl", "bar"})
_OHLC_TRACE_TYPES = frozenset({"candlestick", "ohlc"})

ARTIFACT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "title": "ClientArtifact",
    "description": "An OpenBB Workspace artifact: a chart drawn from rows, or a table.",
    "properties": {
        "type": {"type": "string", "enum": ["chart", "table"]},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "uuid": {"type": "string"},
        "content": {"type": "array", "items": {"type": "object"}},
        "chart_params": {"type": "object"},
    },
    "required": ["type", "name", "description", "uuid", "content"],
}


def _decode(values: Any) -> list[Any]:
    """Return a Plotly data array as a list, decoding typed arrays and their shape."""
    if isinstance(values, list):
        return values
    if not isinstance(values, dict) or "bdata" not in values:
        return []
    code = _TYPED_ARRAY_FORMATS.get(values.get("dtype", "f8"))
    if code is None:
        return []
    raw = base64.b64decode(values["bdata"])
    flat = list(struct.unpack(f"<{len(raw) // struct.calcsize(code)}{code}", raw))
    shape = [int(size) for size in str(values.get("shape", "")).split(",") if size]
    if len(shape) == 2:
        return [flat[row * shape[1] : (row + 1) * shape[1]] for row in range(shape[0])]
    return flat


def _text(value: Any) -> str:
    """Return a Plotly title, given as a string or as ``{"text": ...}``."""
    if isinstance(value, dict):
        value = value.get("text")
    return value if isinstance(value, str) else ""


def is_plotly_figure(value: Any) -> bool:
    """Return whether ``value`` is a serialized Plotly figure."""
    return (
        isinstance(value, dict)
        and isinstance(value.get("layout"), dict)
        and isinstance(value.get("data"), list)
        and all(
            isinstance(trace, dict) and isinstance(trace.get("type"), str)
            for trace in value["data"]
        )
    )


def is_artifact(value: Any) -> bool:
    """Return whether ``value`` is an artifact produced by :func:`figure_to_artifact`."""
    return (
        isinstance(value, dict)
        and value.get("type") in ("chart", "table")
        and isinstance(value.get("content"), list)
        and "uuid" in value
    )


def _series_names(traces: list[dict], reserved: str) -> list[str]:
    """Return a unique, non-empty column name for each trace."""
    names: list[str] = []
    for position, trace in enumerate(traces, start=1):
        base = str(trace.get("name") or f"series {position}")
        name = base
        suffix = 2
        while name in names or name == reserved:
            name = f"{base} ({suffix})"
            suffix += 1
        names.append(name)
    return names


def _xy_chart(traces: list[dict], layout: dict) -> dict | None:
    """Return line, bar, or scatter chart rows and parameters, or None when the traces do not share an axis layout."""
    horizontal = {trace.get("orientation") == "h" for trace in traces}
    if len(horizontal) != 1:
        return None
    category_axis, value_axis = ("y", "x") if horizontal.pop() else ("x", "y")
    x_key = _text((layout.get(f"{category_axis}axis") or {}).get("title")) or "x"
    names = _series_names(traces, x_key)
    rows: dict[Any, dict[str, Any]] = {}
    for name, trace in zip(names, traces, strict=True):
        values = _decode(trace.get(value_axis))
        categories = _decode(trace.get(category_axis)) or list(range(len(values)))
        for category, value in zip(categories, values, strict=False):
            key = (
                category
                if isinstance(category, str | int | float | bool) or category is None
                else json.dumps(category, default=str)
            )
            rows.setdefault(key, {x_key: category})[name] = value
    kinds = {trace["type"] for trace in traces}
    markers_only = all(trace.get("mode") == "markers" for trace in traces)
    numeric_x = all(
        isinstance(row[x_key], int | float) and not isinstance(row[x_key], bool)
        for row in rows.values()
    )
    if kinds == {"bar"}:
        chart_type = "bar"
    elif "bar" not in kinds and markers_only and numeric_x:
        chart_type = "scatter"
    else:
        chart_type = "line"
    return {
        "content": list(rows.values()),
        "chart_params": {"chartType": chart_type, "xKey": x_key, "yKey": names},
    }


def _pie_chart(trace: dict) -> dict:
    """Return pie or donut chart rows and parameters."""
    labels = _decode(trace.get("labels"))
    values = _decode(trace.get("values"))
    chart_type = "donut" if trace.get("hole") else "pie"
    return {
        "content": [
            {"label": label, "value": value}
            for label, value in zip(labels, values, strict=False)
        ],
        "chart_params": {
            "chartType": chart_type,
            "angleKey": "value",
            "calloutLabelKey": "label",
        },
    }


def _table_rows(traces: list[dict]) -> list[dict[str, Any]]:
    """Return every trace's points as long-format rows."""
    rows: list[dict[str, Any]] = []
    for name, trace in zip(_series_names(traces, ""), traces, strict=True):
        base = {"series": name, "trace_type": trace["type"]}
        x = _decode(trace.get("x"))
        y = _decode(trace.get("y"))
        z = _decode(trace.get("z"))
        if z and isinstance(z[0], list):
            rows.extend(
                {
                    **base,
                    "x": x[column] if column < len(x) else column,
                    "y": y[row] if row < len(y) else row,
                    "z": value,
                }
                for row, values in enumerate(z)
                for column, value in enumerate(values)
            )
        elif trace["type"] in _OHLC_TRACE_TYPES:
            fields = {
                key: _decode(trace.get(key)) for key in ("open", "high", "low", "close")
            }
            rows.extend(
                {
                    **base,
                    "x": point,
                    **{
                        key: fields[key][index]
                        for key in fields
                        if index < len(fields[key])
                    },
                }
                for index, point in enumerate(x)
            )
        elif trace.get("labels") is not None:
            rows.extend(
                {**base, "label": label, "value": value}
                for label, value in zip(
                    _decode(trace.get("labels")),
                    _decode(trace.get("values")),
                    strict=False,
                )
            )
        else:
            length = max(len(x), len(y), len(z))
            rows.extend(
                {
                    **base,
                    **{
                        axis: values[index]
                        for axis, values in (("x", x), ("y", y), ("z", z))
                        if index < len(values)
                    },
                }
                for index in range(length)
            )
    return rows


def figure_to_artifact(figure: dict, name: str, description: str) -> dict:
    """Return a Workspace artifact for a serialized Plotly figure.

    Parameters
    ----------
    figure : dict
        The Plotly figure, as produced by ``Figure.to_json``.
    name : str
        The artifact name when the figure has no title.
    description : str
        The artifact description.

    Returns
    -------
    dict
        A ``chart`` artifact for line, bar, scatter, pie, and donut figures, else a ``table`` artifact of the figure's data.
    """
    traces = figure["data"]
    layout = figure["layout"]
    kinds = {trace["type"] for trace in traces}
    chart: dict | None = None
    if len(traces) == 1 and kinds == {"pie"}:
        chart = _pie_chart(traces[0])
    elif traces and kinds <= _XY_TRACE_TYPES:
        chart = _xy_chart(traces, layout)
    artifact: dict[str, Any] = {
        "type": "chart" if chart else "table",
        "name": _text(layout.get("title")) or name,
        "description": description,
        "uuid": str(uuid.uuid4()),
        "content": chart["content"] if chart else _table_rows(traces),
    }
    if chart:
        artifact["chart_params"] = chart["chart_params"]
    return artifact


def convert_figures(payload: Any, tool_name: str) -> Any:
    """Return ``payload`` with any Plotly figure it is, or carries as an OBBject chart, replaced by an artifact.

    Parameters
    ----------
    payload : Any
        A tool result payload.
    tool_name : str
        The name of the tool that produced it.

    Returns
    -------
    Any
        The converted payload, or ``payload`` itself when it holds no figure.
    """
    description = f"Output of the {tool_name} tool."
    if is_plotly_figure(payload):
        return figure_to_artifact(payload, tool_name, description)
    if not isinstance(payload, dict):
        return payload
    chart = payload.get("chart")
    if isinstance(chart, dict) and is_plotly_figure(chart.get("content")):
        return {
            **payload,
            "chart": figure_to_artifact(chart["content"], tool_name, description),
        }
    inner = payload.get("result")
    if isinstance(inner, dict):
        converted = convert_figures(inner, tool_name)
        if converted is not inner:
            return {**payload, "result": converted}
    return payload


def artifact_output_schema(schema: dict | None) -> dict | None:
    """Return an output schema whose OBBject ``chart`` field holds an artifact."""
    if not schema:
        return schema
    properties = schema.get("properties")
    if not isinstance(properties, dict) or "chart" not in properties:
        return schema
    return {
        **schema,
        "properties": {
            **properties,
            "chart": {"anyOf": [ARTIFACT_SCHEMA, {"type": "null"}]},
        },
    }


def _payload(result: ToolResult) -> Any:
    """Return a tool result's structured content, or its text content parsed as JSON."""
    if result.structured_content is not None:
        return result.structured_content
    text = "".join(
        block.text for block in result.content if isinstance(block, TextContent)
    )
    try:
        return json.loads(text)
    except ValueError:
        return None


class ChartArtifactMiddleware(Middleware):
    """Replace Plotly figures in tool results with OpenBB Workspace artifacts."""

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        """Convert the figures in one tool call's result."""
        result = await call_next(context)
        payload = _payload(result)
        converted = convert_figures(payload, context.message.name)
        if converted is payload:
            return result
        return ToolResult(
            content=[TextContent(type="text", text=json.dumps(converted))],
            structured_content=converted,
            meta=result.meta,
        )
