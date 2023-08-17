"""Executive Compensation Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, NonNegativeFloat, PositiveFloat

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class ExecutiveCompensationQueryParams(QueryParams, BaseSymbol):
    """Executive Compensation Query."""


class ExecutiveCompensationData(Data, BaseSymbol):
    """Return Executive Compensation Data."""

    cik: Optional[str] = Field(description="Central Index Key (CIK) of the company.")
    filing_date: dateType = Field(description="Date of the filing.")
    accepted_date: datetime = Field(description="Date the filing was accepted.")
    name_and_position: str = Field(description="Name and position of the executive.")
    year: int = Field(description="Year of the compensation.")
    salary: PositiveFloat = Field(description="Salary of the executive.")
    bonus: NonNegativeFloat = Field(description="Bonus of the executive.")
    stock_award: NonNegativeFloat = Field(description="Stock award of the executive.")
    incentive_plan_compensation: NonNegativeFloat = Field(
        description="Incentive plan compensation of the executive."
    )
    all_other_compensation: NonNegativeFloat = Field(
        description="All other compensation of the executive."
    )
    total: PositiveFloat = Field(description="Total compensation of the executive.")
    url: str = Field(description="URL of the filing data.")
