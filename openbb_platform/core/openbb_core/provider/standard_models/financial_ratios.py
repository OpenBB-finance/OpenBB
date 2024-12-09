"""Financial Ratios Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, NonNegativeInt, field_validator


class FinancialRatiosQueryParams(QueryParams):
    """Financial Ratios Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: NonNegativeInt = Field(
        default=12, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper()


class FinancialRatiosData(Data):
    """Financial Ratios Standard Model."""

    period_ending: str = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    fiscal_period: str = Field(description="Period of the financial ratios.")
    fiscal_year: Optional[int] = Field(default=None, description="Fiscal year.")
