"""Earnings call transcript data model."""


from datetime import datetime
from typing import List, Literal, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class EarningsCallTranscriptQueryParams(QueryParams):
    """Earnings call transcript rating Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    year: int = Field(description="Year of the earnings call transcript.")
    quarter: Literal[1, 2, 3, 4] = Field(
        default=1, description="Quarter of the earnings call transcript."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EarningsCallTranscriptData(Data):
    """Earnings call transcript Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    quarter: int = Field(description="Quarter of the earnings call transcript.")
    year: int = Field(description="Year of the earnings call transcript.")
    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    content: str = Field(description="Content of the earnings call transcript.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
