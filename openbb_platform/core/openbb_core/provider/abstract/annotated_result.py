"""Annotated result."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class AnnotatedResult(BaseModel, Generic[T]):
    """Annotated result allows fetchers to return metadata along with the data."""

    result: T | None = Field(
        default=None,
        description="Serializable results.",
    )
    metadata: dict | None = Field(
        default=None,
        description="Metadata.",
    )
