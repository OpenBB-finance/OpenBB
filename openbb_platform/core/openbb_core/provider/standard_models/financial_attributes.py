"""Financial Attributes Standard Model."""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class FinancialAttributesQueryParams(QueryParams):
    """Financial Attributes Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))
    tag: str = Field(description=QUERY_DESCRIPTIONS.get("tag"))
    period: Literal["annual", "quarter"] | None = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period")
    )
    limit: int | None = Field(default=1000, description=QUERY_DESCRIPTIONS.get("limit"))
    type: str | None = Field(
        default=None, description="Filter by type, when applicable."
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    sort: Literal["asc", "desc"] | None = Field(
        default="desc", description="Sort order."
    )

    @field_validator("period", "sort", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: str | None) -> str | None:
        """Convert field to lowercase."""
        return v.lower() if v else v


class FinancialAttributesData(Data):
    """Financial Attributes Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    value: float | None = Field(default=None, description="The value of the data.")
