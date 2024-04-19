"""Custom field for OpenBB."""

from typing import Any, List, Optional

from pydantic.fields import FieldInfo


class OpenBBField(FieldInfo):
    """Custom field for OpenBB."""

    def __repr__(self):
        """Override FieldInfo __repr__."""
        # We use repr() to avoid decoding special characters like \n
        if self.choices:
            return f"OpenBBField(description={repr(self.description)}, choices={repr(self.choices)})"
        return f"OpenBBField(description={repr(self.description)})"

    def __init__(self, description: str, choices: Optional[List[Any]] = None):
        """Initialize OpenBBField."""
        super().__init__(
            description=description, json_schema_extra={"choices": choices}
        )

    @property
    def choices(self) -> Optional[List[Any]]:
        """Custom choices."""
        return self.json_schema_extra.get("choices")  # type: ignore[union-attr,return-value]
