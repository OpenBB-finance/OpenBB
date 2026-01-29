"""OpenBB 的自定义字段。"""

from typing import Any

from pydantic.fields import FieldInfo


class OpenBBField(FieldInfo):
    """OpenBB 的自定义字段。"""

    def __repr__(self):
        """覆盖 FieldInfo __repr__。"""
        # We use repr() to avoid decoding special characters like \n
        if self.choices:
            return f"OpenBBField(description={repr(self.description)}, choices={repr(self.choices)})"
        return f"OpenBBField(description={repr(self.description)})"

    def __init__(self, description: str, choices: list[Any] | None = None):
        """初始化 OpenBBField。"""
        json_schema_extra = {"choices": choices} if choices else None
        super().__init__(description=description, json_schema_extra=json_schema_extra)  # type: ignore[arg-type]

    @property
    def choices(self) -> list[Any] | None:
        """自定义选项。"""
        if self.json_schema_extra:
            return self.json_schema_extra.get("choices")  # type: ignore[union-attr,return-value]
        return None
