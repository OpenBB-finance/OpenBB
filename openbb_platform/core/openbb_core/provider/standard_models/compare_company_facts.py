"""Compare Company Facts Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CompareCompanyFactsQueryParams(QueryParams):
    """Compare Company Facts Query."""

    symbol: str | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    fact: str = Field(
        default="",
        description="The fact to lookup, typically a GAAP-reporting measure. Choices vary by provider.",
    )


class CompareCompanyFactsData(Data):
    """Compare Company Facts Data."""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    name: str | None = Field(default=None, description="Name of the entity.")
    value: float = Field(
        description="The reported value of the fact or concept.",
    )
    reported_date: dateType | None = Field(
        default=None, description="The date when the report was filed."
    )
    period_beginning: dateType | None = Field(
        default=None,
        description="The start date of the reporting period.",
    )
    period_ending: dateType | None = Field(
        default=None,
        description="The end date of the reporting period.",
    )
    fiscal_year: int | None = Field(
        default=None,
        description="The fiscal year.",
    )
    fiscal_period: str | None = Field(
        default=None,
        description="The fiscal period of the fiscal year.",
    )
