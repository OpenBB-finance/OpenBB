"""ESG Risk Rating Standard Model."""

from typing import List, Literal, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ESGRiskRatingQueryParams(QueryParams):
    """ESG Risk Rating Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class ESGRiskRatingData(Data):
    """ESG Risk Rating Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    cik: str = Field(description=DATA_DESCRIPTIONS.get("cik", ""))
    company_name: str = Field(description="Company name of the company.")
    industry: str = Field(description="Industry of the company.")
    year: int = Field(description="Year of the ESG risk rating.")
    esg_risk_rating: Literal[
        "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"
    ] = Field(description="ESG risk rating of the company.")
    industry_rank: str = Field(description="Industry rank of the company.")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
