"""ESG Score Standard Model."""

from datetime import (
    date as dateType,
)
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ESGScoreQueryParams(QueryParams):
    """ESG Score Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class ESGScoreData(Data):
    """ESG Score Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    cik: Optional[Union[int, str]] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    company_name: Optional[str] = Field(
        default=None, description="Company name of the company."
    )
    environmental_score: Optional[float] = Field(
        default=None, description="Environmental score of the company."
    )
    social_score: Optional[float] = Field(
        default=None, description="Social score of the company."
    )
    governance_score: Optional[float] = Field(
        default=None, description="Governance score of the company."
    )
    esg_score: Optional[float] = Field(
        default=None, description="ESG score of the company."
    )
