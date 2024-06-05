"""Income Statement Growth Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class IncomeStatementGrowthQueryParams(QueryParams):
    """Income Statement Growth Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=10, description=QUERY_DESCRIPTIONS.get("limit", "")
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


class IncomeStatementGrowthData(Data):
    """Income Statement Growth Data."""

    period_ending: dateType = Field(description="The end date of the reporting period.")
    fiscal_period: Optional[str] = Field(
        description="The fiscal period of the report.", default=None
    )
    fiscal_year: Optional[int] = Field(
        description="The fiscal year of the fiscal period.", default=None
    )
