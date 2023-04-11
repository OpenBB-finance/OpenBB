import dataclasses as dc
from typing import Any, Dict, Optional

from pydantic.dataclasses import dataclass

# pylint: disable=too-many-instance-attributes, disable=no-member


@dataclass
class BaseModel:
    def __repr__(self) -> str:
        """Return string representation of model."""
        dataclass_repr = ""
        for key, value in sorted(self.__dict__.items()):
            if key.startswith("_"):
                continue
            dataclass_repr += f"    {key}='{value}', \n"

        return f"{self.__class__.__name__}(\n{dataclass_repr[:-2]}\n)"

    @classmethod
    def get_fields(cls) -> Dict[str, Any]:
        """Get dict of fields."""
        return cls.__dataclass_fields__  # type: ignore

    def get_value(self, field: str) -> Optional[Any]:
        """Get field value."""
        if hasattr(self, field):
            return getattr(self, field)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dict."""
        return dc.asdict(self)  # type: ignore

    def get_default(self, field: str) -> Optional[Any]:
        """Get default field value."""
        if hasattr(self, field):
            return self.get_fields()[field].default
        return None
