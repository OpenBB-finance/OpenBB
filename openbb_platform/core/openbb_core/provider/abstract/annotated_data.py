from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class AnnotatedData(BaseModel, Generic[T]):
    """Annotated data allows fetchers to return metadata along with the data."""

    data: Optional[T] = Field(
        default=None,
        description="Serializable results.",
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Metadata.",
    )
