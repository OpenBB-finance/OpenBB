"""Wire-format models for the NDJSON dispatcher protocol."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Request(BaseModel):
    """One request line on the NDJSON stream."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = Field(
        default=None,
        description="Opaque correlation id echoed on the response. Generated client-side.",
    )
    command: str = Field(
        description="Dotted command path, e.g. 'economy.gdp' or 'equity.price.historical'.",
    )
    params: dict[str, Any] = Field(default_factory=dict)


class ResponseError(BaseModel):
    """Structured error attached to a failed Response."""

    model_config = ConfigDict(extra="forbid")

    type: str
    message: str


class Response(BaseModel):
    """One response line on the NDJSON stream."""

    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    ok: bool
    result: Any = None
    error: ResponseError | None = None
