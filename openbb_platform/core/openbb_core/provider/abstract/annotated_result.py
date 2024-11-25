"""Annotated result."""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class AnnotatedResult(BaseModel, Generic[T]):
    """Annotated result allows fetchers to return metadata along with the data."""

    result: Optional[T] = Field(
        default=None,
        description="Serializable results.",
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Metadata.",
    )
