"""World News Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Dict, List, Optional

from dateutil.relativedelta import relativedelta
from pydantic import Field, NonNegativeInt, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class WorldNewsQueryParams(QueryParams):
    """World News Query."""

    limit: NonNegativeInt = Field(
        default=20,
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " Here its the no. of articles to return.",
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )

    @field_validator("start_date", mode="before")
    @classmethod
    def start_date_validate(cls, v) -> dateType:  # pylint: disable=E0213
        """Populate start date if empty."""
        if not v:
            now = datetime.now().date()
            v = now - relativedelta(years=1)
        return v

    @field_validator("end_date", mode="before")
    @classmethod
    def end_date_validate(cls, v) -> dateType:  # pylint: disable=E0213
        """Populate end date if empty."""
        if not v:
            v = datetime.now().date()
        return v


class WorldNewsData(Data):
    """World News Data."""

    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + " Here it is the published date of the news."
    )
    title: str = Field(description="Title of the news.")
    images: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Images associated with the news."
    )
    text: Optional[str] = Field(default=None, description="Text/body of the news.")
    url: Optional[str] = Field(default=None, description="URL of the news.")
