"""ESG Score data model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class ESGScoreQueryParams(QueryParams):
    """ESG score query model."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class ESGScoreData(Data):
    """ESG Score data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    cik: str = Field(description="CIK of the company.")
    company_name: str = Field(description="Company name of the company.")
    form_type: str = Field(description="Form type of the company.")
    accepted_date: datetime = Field(description="Accepted date of the company.")
    date: dateType = Field(description="Date of the fetched score.")
    environmental_score: float = Field(
        description="Environmental score of the company."
    )
    social_score: float = Field(description="Social score of the company.")
    governance_score: float = Field(description="Governance score of the company.")
    esg_score: float = Field(description="ESG score of the company.")
    url: str = Field(description="URL of the company.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
