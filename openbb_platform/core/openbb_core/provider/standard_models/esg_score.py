"""ESG Score Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EsgScoreQueryParams(QueryParams):
    """ESG Score Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EsgScoreData(Data):
    """ESG Score Data."""

    period_ending: dateType = Field(description="Period ending date of the report.")
    disclosure_date: dateType | datetime | None = Field(
        description="Date when the report was submitted."
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
        coerce_numbers_to_str=True,
    )
    company_name: str | None = Field(
        default=None, description="Company name of the company."
    )
    form_type: str | None = Field(
        default=None, description="Form type where the disclosure was made."
    )
    environmental_score: float = Field(
        description="Environmental score of the company."
    )
    social_score: float = Field(description="Social score of the company.")
    governance_score: float = Field(description="Governance score of the company.")
    esg_score: float = Field(description="ESG score of the company.")
    url: str | None = Field(default=None, description="URL to the report or filing.")
