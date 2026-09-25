"""Server-side tool pipelines for the OpenBB MCP server."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Annotated, Any

from fastmcp.exceptions import ToolError
from mcp.types import TextContent
from pydantic import Field

from openbb_mcp_server.app.artifacts import is_artifact
from openbb_mcp_server.models.tools import PipelineStep

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from fastmcp.tools.base import ToolResult

PIPELINE_TOOL_NAME = "run_pipeline"

PIPELINE_DESCRIPTION = (
    "Run tools in sequence on the server, feeding the `results` of earlier steps (their"
    " whole output when they have none) into the arguments of later ones, so data"
    " such as a price history never passes"
    " through the conversation. Use it to chain a data tool into a data-processing"
    " tool (technical, quantitative, econometrics), which takes its input rows as"
    " `data`. Each step names a `tool`, its `arguments`, an optional `id`, and"
    " `inputs` mapping argument names to earlier step ids. Returns the output of the"
    " last step, or of the steps listed in `outputs`, keyed by step id (or position)."
    ' Example: steps=[{"id": "prices", "tool": "equity_price_historical",'
    ' "arguments": {"symbol": "AAPL", "provider": "yfinance"}},'
    ' {"tool": "technical_rsi", "arguments": {"length": 14},'
    ' "inputs": {"data": "prices"}}].'
)


def _tool_output(result: ToolResult) -> Any:
    """Return a tool result's structured output, or its text content parsed as JSON when possible."""
    if result.structured_content is not None:
        return result.structured_content
    text = "".join(
        block.text for block in result.content if isinstance(block, TextContent)
    )
    try:
        return json.loads(text)
    except ValueError:
        return text


def _results_of(output: Any) -> Any:
    """Return an output's ``results`` field, an artifact's rows, its lone wrapped ``result``, or the output itself."""
    if is_artifact(output):
        return output["content"]
    if isinstance(output, dict):
        if "results" in output:
            return output["results"]
        if set(output) == {"result"}:
            return output["result"]
    return output


def register_pipeline_tool(mcp: FastMCP) -> None:
    """Register the ``run_pipeline`` tool on ``mcp``.

    Parameters
    ----------
    mcp : FastMCP
        The server whose tools the pipeline calls.
    """

    @mcp.tool(
        name=PIPELINE_TOOL_NAME,
        description=PIPELINE_DESCRIPTION,
        tags={"admin"},
    )
    async def run_pipeline(
        steps: Annotated[
            list[PipelineStep],
            Field(min_length=1, description="The tool calls to run, in order."),
        ],
        outputs: Annotated[
            list[str] | None,
            Field(
                description="Ids (or positions) of the steps whose outputs are"
                " returned. Defaults to the last step."
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Run tools in sequence, passing earlier results into later arguments."""
        keys = [step.id or str(position) for position, step in enumerate(steps)]
        if len(set(keys)) != len(keys):
            raise ToolError("Step ids must be unique.")
        for position, (key, step) in enumerate(zip(keys, steps, strict=True)):
            if step.tool == PIPELINE_TOOL_NAME:
                raise ToolError(f"Step {key!r} cannot call {PIPELINE_TOOL_NAME}.")
            for argument, source in step.inputs.items():
                if source not in keys[:position]:
                    raise ToolError(
                        f"Step {key!r} input {argument!r} refers to {source!r},"
                        " which is not an earlier step."
                    )
        selected = outputs or [keys[-1]]
        unknown = [key for key in selected if key not in keys]
        if unknown:
            raise ToolError(f"Unknown output steps: {', '.join(unknown)}.")

        produced: dict[str, Any] = {}
        for key, step in zip(keys, steps, strict=True):
            arguments = dict(step.arguments)
            for argument, source in step.inputs.items():
                arguments[argument] = _results_of(produced[source])
            try:
                result = await mcp.call_tool(step.tool, arguments)
            except Exception as exc:
                raise ToolError(f"Step {key!r} ({step.tool}) failed: {exc}") from exc
            produced[key] = _tool_output(result)
        return {key: produced[key] for key in selected}
