from datetime import datetime
from typing import Any, Dict, List

from pydantic import Field

from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.modelobbject import OBBject


class JournalEntry(Tagged):
    journal_id: str = Field(description="Id of the Journal.")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments of the command.",
    )
    duration: int = Field(
        description="Execution duration in nano second of the command."
    )
    output: OBBject = Field(description="Output of the command.")
    route: str = Field(description="Route of the command.")
    timestamp: datetime = Field(description="Execution starting timestamp.")
    alias_list: List[str] = Field(
        default_factory=list,
        description="List of alias to find a JournalEntry easier than with it's `tag`.",
    )

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
        )
