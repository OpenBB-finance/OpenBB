"""Custom field for OpenBB."""

from typing import Any

from pydantic.fields import FieldInfo


class OpenBBField(FieldInfo):
    """Custom field for OpenBB."""

    def __repr__(self):
        """Override FieldInfo __repr__."""
        # We use repr() to avoid decoding special characters like \n
        if self.choices:
            return f"OpenBBField(description={repr(self.description)}, choices={repr(self.choices)})"
        return f"OpenBBField(description={repr(self.description)})"

    def __init__(self, description: str, choices: list[Any] | None = None):
        """Initialize OpenBBField."""
        json_schema_extra = {"choices": choices} if choices else None
        super().__init__(description=description, json_schema_extra=json_schema_extra)  # type: ignore[arg-type]

    @property
    def choices(self) -> list[Any] | None:
        """Custom choices."""
        if self.json_schema_extra:
            return self.json_schema_extra.get("choices")  # type: ignore[union-attr,return-value]
        return None
