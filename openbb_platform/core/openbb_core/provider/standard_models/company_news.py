"""Company News Standard Model."""


from datetime import datetime
from typing import Optional

from pydantic import Field, NonNegativeInt, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class CompanyNewsQueryParams(QueryParams):
    """Company news Query."""

    symbols: str = Field(
        min_length=1,
        description=QUERY_DESCRIPTIONS.get("symbols", "")
        + " Here it is a separated list of symbols.",
    )
    limit: Optional[NonNegativeInt] = Field(
        default=20, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbols", mode="before")
    @classmethod
    def symbols_validate(cls, v: str):  # pylint: disable=E0213
        """Validate the symbols."""
        return v.upper()


class CompanyNewsData(Data):
    """Company News Data."""

    symbols: str = Field(
        min_length=1,
        description=DATA_DESCRIPTIONS.get("symbols", "")
        + " Here it is a separated list of symbols.",
    )
    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + " Here it is the date of the news."
    )
    title: str = Field(description="Title of the news.")
    image: Optional[str] = Field(default=None, description="Image URL of the news.")
    text: Optional[str] = Field(default=None, description="Text/body of the news.")
    url: str = Field(description="URL of the news.")
