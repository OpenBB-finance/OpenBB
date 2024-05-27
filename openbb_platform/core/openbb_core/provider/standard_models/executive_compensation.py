"""Executive Compensation Standard Model."""

from typing import Optional

from pydantic import Field, NonNegativeFloat, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ExecutiveCompensationQueryParams(QueryParams):
    """Executive Compensation Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class ExecutiveCompensationData(Data):
    """Executive Compensation Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    company_name: Optional[str] = Field(
        default=None, description="The name of the company."
    )
    industry: Optional[str] = Field(
        default=None, description="The industry of the company."
    )
    year: Optional[int] = Field(default=None, description="Year of the compensation.")
    name_and_position: Optional[str] = Field(
        default=None, description="Name and position."
    )
    salary: Optional[NonNegativeFloat] = Field(default=None, description="Salary.")
    bonus: Optional[NonNegativeFloat] = Field(
        default=None, description="Bonus payments."
    )
    stock_award: Optional[NonNegativeFloat] = Field(
        default=None, description="Stock awards."
    )
    incentive_plan_compensation: Optional[NonNegativeFloat] = Field(
        default=None, description="Incentive plan compensation."
    )
    all_other_compensation: Optional[NonNegativeFloat] = Field(
        default=None, description="All other compensation."
    )
    total: Optional[NonNegativeFloat] = Field(
        default=None, description="Total compensation."
    )
