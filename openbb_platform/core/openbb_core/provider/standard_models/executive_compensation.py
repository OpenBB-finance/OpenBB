"""Executive Compensation Standard Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

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
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class ExecutiveCompensationData(Data):
    """Executive Compensation Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: Optional[Union[int, str]] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    filing_date: Optional[dateType] = Field(
        default=None, description="Date of the filing."
    )
    accepted_date: Optional[datetime] = Field(
        default=None, description="Date the filing was accepted."
    )
    name_and_position: Optional[str] = Field(
        default=None, description="Name and position of the executive."
    )
    year: Optional[int] = Field(default=None, description="Year of the compensation.")
    salary: Optional[float] = Field(
        default=None, description="Salary of the executive."
    )
    bonus: Optional[float] = Field(default=None, description="Bonus of the executive.")
    stock_award: Optional[float] = Field(
        default=None, description="Stock award of the executive."
    )
    incentive_plan_compensation: Optional[float] = Field(
        default=None, description="Incentive plan compensation of the executive."
    )
    all_other_compensation: Optional[float] = Field(
        default=None, description="All other compensation of the executive."
    )
    total: Optional[float] = Field(
        default=None, description="Total compensation of the executive."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
