"""Financial Attributes Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class FinancialAttributesQueryParams(QueryParams):
    """Financial Attributes Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description=QUERY_DESCRIPTIONS.get("tag"))
    period: Optional[Literal["annual", "quarter"]] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period")
    )
    limit: Optional[int] = Field(
        default=1000, description=QUERY_DESCRIPTIONS.get("limit")
    )
    type: Optional[str] = Field(
        default=None, description="Filter by type, when applicable."
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    sort: Optional[Literal["asc", "desc"]] = Field(
        default="desc", description="Sort order."
    )

    @field_validator("period", "sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class FinancialAttributesData(Data):
    """Financial Attributes Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    value: Optional[float] = Field(default=None, description="The value of the data.")
