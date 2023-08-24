from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments of the command.",
    )
    duration: int = Field(
        description="Execution duration in nano second of the command."
    )
    route: str = Field(description="Route of the command.")
    timestamp: datetime = Field(description="Execution starting timestamp.")

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )
