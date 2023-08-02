"""Executive Compensation Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field, NonNegativeFloat, PositiveFloat

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol


class ExecutiveCompensationQueryParams(QueryParams, BaseSymbol):
    """Executive Compensation Query."""


class ExecutiveCompensationData(Data, BaseSymbol):
    """Return Executive Compensation Data."""

    cik: Optional[str] = Field(
        description="The Central Index Key (CIK) of the company."
    )
    filing_date: dateType = Field(description="The date of the filing.")
    accepted_date: datetime = Field(description="The date the filing was accepted.")
    name_and_position: str = Field(
        description="The name and position of the executive."
    )
    year: int = Field(description="The year of the compensation.")
    salary: PositiveFloat = Field(description="The salary of the executive.")
    bonus: NonNegativeFloat = Field(description="The bonus of the executive.")
    stock_award: NonNegativeFloat = Field(
        description="The stock award of the executive."
    )
    incentive_plan_compensation: NonNegativeFloat = Field(
        description="The incentive plan compensation of the executive."
    )
    all_other_compensation: NonNegativeFloat = Field(
        description="The all other compensation of the executive."
    )
    total: PositiveFloat = Field(description="The total compensation of the executive.")
    url: str = Field(description="The URL of the filing data.")
