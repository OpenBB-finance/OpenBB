"""Major Indices Constituents data model."""


from datetime import date
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class MajorIndicesConstituentsQueryParams(QueryParams):
    """Major Indices Constituents Query."""

    index: Literal["nasdaq", "sp500", "dowjones"] = Field(
        default="dowjones",
        description="Index for which we want to fetch the constituents.",
    )


class MajorIndicesConstituentsData(Data):
    """Major Indices Constituents Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="Name of the constituent company in the index.")
    sector: str = Field(
        description="Sector the constituent company in the index belongs to."
    )
    sub_sector: Optional[str] = Field(
        description="Sub-sector the constituent company in the index belongs to."
    )
    headquarter: Optional[str] = Field(
        description="Location of the headquarter of the constituent company in the index."
    )
    date_first_added: Optional[Union[date, str]] = Field(
        description="Date the constituent company was added to the index."
    )
    cik: int = Field(
        description="Central Index Key of the constituent company in the index."
    )
    founded: Union[date, str] = Field(
        description="Founding year of the constituent company in the index."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
