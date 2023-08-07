from pydantic import ConfigDict, BaseModel, Field


class JournalQuery(BaseModel):
    journal_entry_id: str = Field(
        default="",
        description="Tag of the JournalEntry to search for.",
    )
    ignore_error_output: bool = Field(
        default=True,
        description="Whether or not the JournalEntry with an CommandOutput.Error should be ignored.",
    )

    model_config = ConfigDict(frozen=True)
