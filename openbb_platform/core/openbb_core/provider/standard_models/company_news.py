"""Company News Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

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

    symbol: str = Field(
        min_length=1,
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " This endpoint will accept multiple symbols separated by commas.",
    )
    limit: Optional[NonNegativeInt] = Field(
        default=20, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def symbols_validate(cls, v: str) -> str:  # pylint: disable=E0213
        """Validate the symbols."""
        return v.upper()

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
