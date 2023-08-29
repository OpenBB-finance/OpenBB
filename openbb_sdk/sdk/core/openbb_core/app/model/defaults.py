from typing import Dict, Optional

from pydantic import BaseModel, Field


class Defaults(BaseModel):
    """Defaults."""

    class Config:
        validate_assignment = True

    routes: Dict[str, Dict[str, Optional[str]]] = Field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.dict().items()
        )
