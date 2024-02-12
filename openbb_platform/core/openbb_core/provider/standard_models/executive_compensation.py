"""Executive Compensation Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional, Set, Union

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
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class ExecutiveCompensationData(Data):
    """Executive Compensation Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    filing_date: dateType = Field(description="Date of the filing.")
    accepted_date: datetime = Field(description="Date the filing was accepted.")
    name_and_position: str = Field(description="Name and position of the executive.")
    year: int = Field(description="Year of the compensation.")
    salary: NonNegativeFloat = Field(description="Salary of the executive.")
    bonus: NonNegativeFloat = Field(description="Bonus of the executive.")
    stock_award: NonNegativeFloat = Field(description="Stock award of the executive.")
    incentive_plan_compensation: NonNegativeFloat = Field(
        description="Incentive plan compensation of the executive."
    )
    all_other_compensation: NonNegativeFloat = Field(
        description="All other compensation of the executive."
    )
    total: NonNegativeFloat = Field(description="Total compensation of the executive.")
    url: str = Field(description="URL of the filing data.")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
