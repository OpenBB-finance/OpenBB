"""带注释的结果。"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class AnnotatedResult(BaseModel, Generic[T]):
    """带注释的结果允许 fetcher 将元数据与数据一起返回。"""

    result: T | None = Field(
        default=None,
        description="可序列化的结果。",
    )
    metadata: dict | None = Field(
        default=None,
        description="元数据。",
    )
