"""Historical Attributes Standard Model."""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class HistoricalAttributesQueryParams(QueryParams):
    """Historical Attributes Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description="Intrinio data tag ID or code.")
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    frequency: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] | None = (
        Field(default="yearly", description=QUERY_DESCRIPTIONS.get("frequency"))
    )
    limit: int | None = Field(default=1000, description=QUERY_DESCRIPTIONS.get("limit"))
    tag_type: str | None = Field(
        default=None, description="Filter by type, when applicable."
    )
    sort: Literal["asc", "desc"] | None = Field(
        default="desc", description="Sort order."
    )

    @field_validator("tag", mode="before", check_fields=False)
    @classmethod
    def multiple_tags(cls, v: str | list[str] | set[str]):
        """Accept a comma-separated string or list of tags."""
        if isinstance(v, str):
            return v.lower()
        return ",".join([tag.lower() for tag in list(v)])

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()

    @field_validator("frequency", "sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """Convert field to lowercase."""
        return v.lower() if v else v


class HistoricalAttributesData(Data):
    """Historical Attributes Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol"))
    tag: str | None = Field(default=None, description="Tag name for the fetched data.")
    value: float | None = Field(default=None, description="The value of the data.")
