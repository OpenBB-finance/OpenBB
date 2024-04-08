"""Revenue by Business Line Standard Model."""

from datetime import date as dateType
from typing import Dict, Literal, Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)


class RevenueBusinessLineQueryParams(QueryParams):
    """Revenue by Business Line Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Literal["quarter", "annual"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    structure: Literal["hierarchical", "flat"] = Field(
        default="flat", description="Structure of the returned data."
    )  # should always be flat

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper()

    @field_validator("period", "structure", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class RevenueBusinessLineData(Data):
    """Revenue by Business Line Data."""

    period_ending: dateType = Field(description="The end date of the reporting period.")
    fiscal_period: Optional[str] = Field(
        default=None, description="The fiscal period of the reporting period."
    )
    fiscal_year: Optional[int] = Field(
        default=None, description="The fiscal year of the reporting period."
    )
    filing_date: Optional[dateType] = Field(
        default=None, description="The filing date of the report."
    )
    business_line: Dict[str, ForceInt] = Field(
        description="Dictionary containing the revenue of the business line."
    )
