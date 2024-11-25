"""Reported Financials."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator, model_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)


class ReportedFinancialsQueryParams(QueryParams):
    """Reported Financials Query Params."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    statement_type: str = Field(
        default="balance",
        description="The type of financial statement - i.e, balance, income, cash.",
    )
    limit: Optional[int] = Field(
        default=100,
        description=(
            QUERY_DESCRIPTIONS.get("limit", "")
            + " Although the response object contains multiple results,"
            + " because of the variance in the fields, year-to-year and quarter-to-quarter,"
            + " it is recommended to view results in small chunks."
        ),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper()

    @field_validator("period", "statement_type", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class ReportedFinancialsData(Data):
    """Reported Financials Data."""

    period_ending: dateType = Field(
        description="The ending date of the reporting period."
    )
    fiscal_period: str = Field(
        description="The fiscal period of the report (e.g. FY, Q1, etc.)."
    )
    fiscal_year: Optional[int] = Field(
        description="The fiscal year of the fiscal period.", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )
