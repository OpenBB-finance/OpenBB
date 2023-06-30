from typing import List

from pydantic import Field

from openbb_sdk_core.app.model.abstract.tagged import Tagged


class Journal(Tagged):
    name: str = Field(default="Untitled", description="Name of the Report.")
    journal_entry_id_list: List[str] = Field(
        default_factory=list,
        description="Ordered list of JournalEntry ids.",
    )
