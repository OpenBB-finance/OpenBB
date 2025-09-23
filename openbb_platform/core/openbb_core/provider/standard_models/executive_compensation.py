"""Executive Compensation Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


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
    report_date: Optional[dateType] = Field(
        default=None, description="Date of reported compensation."
    )
    company_name: Optional[str] = Field(
        default=None, description="The name of the company."
    )
    executive: Optional[str] = Field(default=None, description="Name and position.")
    year: Optional[int] = Field(default=None, description="Year of the compensation.")
    salary: Optional[Union[int, float]] = Field(
        default=None, description="Base salary."
    )
    bonus: Optional[Union[int, float]] = Field(
        default=None, description="Bonus payments."
    )
    stock_award: Optional[Union[int, float]] = Field(
        default=None, description="Stock awards."
    )
    option_award: Optional[Union[int, float]] = Field(
        default=None, description="Option awards."
    )
    incentive_plan_compensation: Optional[Union[int, float]] = Field(
        default=None, description="Incentive plan compensation."
    )
    all_other_compensation: Optional[Union[int, float]] = Field(
        default=None, description="All other compensation."
    )
    total: Optional[Union[int, float]] = Field(
        default=None, description="Total compensation."
    )
