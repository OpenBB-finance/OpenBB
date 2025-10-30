"""Executive Compensation Standard Model."""

from datetime import date as dateType

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
    cik: str | None = Field(default=None, description=DATA_DESCRIPTIONS.get("cik", ""))
    report_date: dateType | None = Field(
        default=None, description="Date of reported compensation."
    )
    company_name: str | None = Field(
        default=None, description="The name of the company."
    )
    executive: str | None = Field(default=None, description="Name and position.")
    year: int | None = Field(default=None, description="Year of the compensation.")
    salary: int | float | None = Field(default=None, description="Base salary.")
    bonus: int | float | None = Field(default=None, description="Bonus payments.")
    stock_award: int | float | None = Field(default=None, description="Stock awards.")
    option_award: int | float | None = Field(default=None, description="Option awards.")
    incentive_plan_compensation: int | float | None = Field(
        default=None, description="Incentive plan compensation."
    )
    all_other_compensation: int | float | None = Field(
        default=None, description="All other compensation."
    )
    total: int | float | None = Field(default=None, description="Total compensation.")
