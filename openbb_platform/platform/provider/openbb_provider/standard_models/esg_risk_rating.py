"""ESG Risk Rating data model."""


from typing import List, Literal, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class ESGRiskRatingQueryParams(QueryParams):
    """ESG risk rating query model."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class ESGRiskRatingData(Data):
    """ESG Risk Rating data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    cik: str = Field(description="CIK of the company.")
    company_name: str = Field(description="Company name of the company.")
    industry: str = Field(description="Industry of the company.")
    year: int = Field(description="Year of the ESG risk rating.")
    esg_risk_rating: Literal[
        "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"
    ] = Field(description="ESG risk rating of the company.")
    industry_rank: str = Field(description="Industry rank of the company.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
