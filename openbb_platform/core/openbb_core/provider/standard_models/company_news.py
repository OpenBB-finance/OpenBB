"""Company News Standard Model."""

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


class CompanyNewsQueryParams(QueryParams):
    """Company news Query."""

    symbol: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("symbol", ""),
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    limit: Optional[NonNegativeInt] = Field(
        default=2500, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def symbols_validate(cls, v):
        """Validate the symbols."""
        return v.upper() if v else None

    @field_validator("start_date", mode="before")
    @classmethod
    def start_date_validate(cls, v) -> dateType:  # pylint: disable=E0213
        """Populate start date if empty."""
        if not v:
            now = datetime.now().date()
            v = now - relativedelta(weeks=16)
        return v

    @field_validator("end_date", mode="before")
    @classmethod
    def end_date_validate(cls, v) -> dateType:  # pylint: disable=E0213
        """Populate end date if empty."""
        if not v:
            v = datetime.now().date()
        return v


class CompanyNewsData(Data):
    """Company News Data."""

    date: datetime = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + " Here it is the published date of the article."
    )
    title: str = Field(description="Title of the article.")
    text: Optional[str] = Field(default=None, description="Text/body of the article.")
    images: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Images associated with the article."
    )
    url: str = Field(description="URL to the article.")
    symbols: Optional[str] = Field(
        default=None, description="Symbols associated with the article."
    )
