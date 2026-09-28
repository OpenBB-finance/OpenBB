"""Deterministic commands under the ``mcp_fixture`` router."""

from typing import Annotated

from fastapi import Query
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

router = Router(prefix="", description="Deterministic commands for MCP server tests.")


class EchoRow(Data):
    """One echoed row."""

    symbol: str = Field(description="The requested symbol.")
    index: int = Field(description="Zero-based position of the row.")


@router.command(methods=["GET"])
async def echo(
    symbol: Annotated[str, Query(description="Symbol to echo back.")] = "AAPL",
    rows: Annotated[int, Query(description="Number of rows to return.", ge=1)] = 1,
) -> OBBject[list[EchoRow]]:
    """Return deterministic rows for a symbol."""
    return OBBject(results=[EchoRow(symbol=symbol, index=i) for i in range(rows)])


@router.command(methods=["GET"])
async def fail(
    message: Annotated[
        str, Query(description="Message of the raised error.")
    ] = "fixture failure",
) -> OBBject[list[EchoRow]]:
    """Raise an OpenBBError with the given message."""
    raise OpenBBError(message)


class ScaleQueryParams(QueryParams):
    """Query parameters for the ``scale`` command."""

    data: list[Data] = Field(description="Rows carrying a numeric ``index`` column.")
    factor: float = Field(default=2.0, description="Multiplier applied to ``index``.")


class ScaledRow(Data):
    """One scaled row."""

    symbol: str = Field(description="The row's symbol.")
    value: float = Field(description="The row's ``index`` times ``factor``.")


@router.command(methods=["POST"])
def scale(params: ScaleQueryParams) -> OBBject[list[ScaledRow]]:
    """Multiply the ``index`` of every row by ``factor``."""
    return OBBject(
        results=[
            ScaledRow(symbol=row.symbol, value=row.index * params.factor)
            for row in params.data
        ]
    )
