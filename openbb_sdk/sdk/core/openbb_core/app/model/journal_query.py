from pydantic import BaseModel, Field


class JournalQuery(BaseModel):
    journal_entry_id: str = Field(
        default="",
        description="Tag of the JournalEntry to search for.",
    )
    ignore_error_output: bool = Field(
        default=True,
        description="Whether or not the JournalEntry with an OBBject.Error should be ignored.",
    )

    class Config:
        allow_mutation = False
