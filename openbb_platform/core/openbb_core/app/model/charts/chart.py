"""OpenBB Core 图表模型。"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Chart(BaseModel):
    """图表模型。"""

    content: dict[str, Any] | None = Field(
        default=None,
        description="图表的原始文本表示。",
    )
    format: str | None = Field(
        default=None,
        description="`content` 属性的补充属性。它指定图表的格式。",
    )
    fig: Any | None = Field(
        default=None,
        description="Figure 对象。",
        json_schema_extra={"exclude_from_api": True},
    )
    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        """返回字符串表示形式。"""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
