"""Forward EBITDA Estimates Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data, ForceInt
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ForwardEbitdaEstimatesQueryParams(QueryParams):
    """Forward EBITDA Estimates Query Parameters."""

    symbol: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["symbol"],
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert field to uppercase."""
        return v.upper() if v else None


class ForwardEbitdaEstimatesData(Data):
    """Forward EBITDA Estimates Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(default=None, description="Name of the entity.")
    last_updated: Optional[dateType] = Field(
        default=None,
        description="The date of the last update.",
    )
    period_ending: Optional[dateType] = Field(
        default=None,
        description="The end date of the reporting period.",
    )
    fiscal_year: Optional[int] = Field(
        default=None, description="Fiscal year for the estimate."
    )
    fiscal_period: Optional[str] = Field(
        default=None, description="Fiscal quarter for the estimate."
    )
    calendar_year: Optional[int] = Field(
        default=None, description="Calendar year for the estimate."
    )
    calendar_period: Optional[Union[int, str]] = Field(
        default=None, description="Calendar quarter for the estimate."
    )
    low_estimate: Optional[ForceInt] = Field(
        default=None, description="The EBITDA estimate low for the period."
    )
    high_estimate: Optional[ForceInt] = Field(
        default=None, description="The EBITDA estimate high for the period."
    )
    mean: Optional[ForceInt] = Field(
        default=None, description="The EBITDA estimate mean for the period."
    )
    median: Optional[ForceInt] = Field(
        default=None, description="The EBITDA estimate median for the period."
    )
    standard_deviation: Optional[ForceInt] = Field(
        default=None,
        description="The EBITDA estimate standard deviation for the period.",
    )
    number_of_analysts: Optional[int] = Field(
        default=None,
        description="Number of analysts providing estimates for the period.",
    )
