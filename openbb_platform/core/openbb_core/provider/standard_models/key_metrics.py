"""Key Metrics Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class KeyMetricsQueryParams(QueryParams):
    """Key Metrics Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Optional[str] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: Optional[int] = Field(
        default=100, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()

    @field_validator("period", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class KeyMetricsData(Data):
    """Key Metrics Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    period_ending: Optional[dateType] = Field(
        default=None, description="Data for the fiscal period ending."
    )
    fiscal_year: Optional[int] = Field(
        default=None, description="Fiscal year of the fiscal period."
    )
    fiscal_period: Optional[str] = Field(
        default=None, description="Fiscal period of the fiscal year."
    )
    market_cap: Optional[ForceInt] = Field(
        default=None, description="Market capitalization"
    )
    pe_ratio: Optional[float] = Field(
        default=None, description="Price-to-earnings ratio (P/E ratio)"
    )
