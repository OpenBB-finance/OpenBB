"""Custom field for OpenBB."""

from typing import Any

from pydantic.config import JsonDict, JsonValue
from pydantic.fields import FieldInfo


class OpenBBField(FieldInfo):  # ty: ignore[subclass-of-final-class]
    """Custom field for OpenBB."""

    def __repr__(self):
        """Override FieldInfo __repr__."""
        # We use repr() to avoid decoding special characters like \n
        if self.choices:
            return f"OpenBBField(description={repr(self.description)}, choices={repr(self.choices)})"
        return f"OpenBBField(description={repr(self.description)})"

    def __init__(self, description: str, choices: list[JsonValue] | None = None):
        """Initialize OpenBBField."""
        json_schema_extra: JsonDict | None = {"choices": choices} if choices else None
        super().__init__(description=description, json_schema_extra=json_schema_extra)

    @property
    def choices(self) -> list[Any] | None:
        """Custom choices."""
        if isinstance(self.json_schema_extra, dict):
            choices = self.json_schema_extra.get("choices")
            if isinstance(choices, list):
                return choices
        return None
