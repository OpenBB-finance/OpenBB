from typing import Any, Optional

from pydantic.dataclasses import dataclass

# pylint: disable=too-many-instance-attributes, disable=no-member


@dataclass
class BaseModel:
    def __repr__(self) -> str:
        """Return string representation of model."""
        dataclass_repr = ""
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            dataclass_repr += f"    {key}='{value}', \n"

        return f"{self.__class__.__name__}(\n{dataclass_repr[:-2]}\n)"

    @classmethod
    def get_fields(cls) -> dict[str, Any]:
        """Get dict of fields."""
        return cls.__dataclass_fields__  # type: ignore

    def get_field_value(self, field: str) -> Optional[str]:
        """Get field value."""
        if hasattr(self, field):
            return getattr(self, field)
        return None
