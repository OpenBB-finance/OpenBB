"""Historical Attributes Standard Model."""

from datetime import date as dateType
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class HistoricalAttributesQueryParams(QueryParams):
    """Historical Attributes Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description="Intrinio data tag ID or code.")
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    frequency: Optional[
        Literal["daily", "weekly", "monthly", "quarterly", "yearly"]
    ] = Field(default="yearly", description=QUERY_DESCRIPTIONS.get("frequency"))
    limit: Optional[int] = Field(
        default=1000, description=QUERY_DESCRIPTIONS.get("limit")
    )
    tag_type: Optional[str] = Field(
        default=None, description="Filter by type, when applicable."
    )
    sort: Optional[Literal["asc", "desc"]] = Field(
        default="desc", description="Sort order."
    )

    @field_validator("tag", mode="before", check_fields=False)
    @classmethod
    def multiple_tags(cls, v: Union[str, List[str], Set[str]]):
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
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class HistoricalAttributesData(Data):
    """Historical Attributes Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol"))
    tag: Optional[str] = Field(
        default=None, description="Tag name for the fetched data."
    )
    value: Optional[float] = Field(default=None, description="The value of the data.")
