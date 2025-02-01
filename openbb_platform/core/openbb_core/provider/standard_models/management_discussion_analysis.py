"""Management Discussion & Analysis Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ManagementDiscussionAnalysisQueryParams(QueryParams):
    """Management Discussion & Analysis Query Parameters."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    calendar_year: Optional[int] = Field(
        default=None,
        description="Calendar year of the report. By default, is the current year."
        + " If the calendar period is not provided, but the calendar year is, it will return the annual report.",
    )
    calendar_period: Optional[Literal["Q1", "Q2", "Q3", "Q4"]] = Field(
        default=None,
        description="Calendar period of the report. By default, is the most recent report available for the symbol."
        + " If no calendar year and no calendar period are provided, it will return the most recent report.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper()


class ManagementDiscussionAnalysisData(Data):
    """Management Discussion & Analysis Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    calendar_year: int = Field(description="The calendar year of the report.")
    calendar_period: int = Field(description="The calendar period of the report.")
    period_ending: Optional[dateType] = Field(
        description="The end date of the reporting period.", default=None
    )
    content: str = Field(
        description="The content of the management discussion and analysis."
    )
