from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class Defaults(BaseModel):
    """Defaults."""

    model_config = ConfigDict(validate_assignment=True)

    routes: Dict[str, Dict[str, Optional[str]]] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
