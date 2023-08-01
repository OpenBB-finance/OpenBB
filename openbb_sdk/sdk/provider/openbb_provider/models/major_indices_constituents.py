"""Major Indices Constituents data model."""


from datetime import date
from typing import Literal, Optional, Union

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol

from pydantic import Field


class MajorIndicesConstituentsQueryParams(QueryParams):
    """Major Indices Constituents Query."""

    index: Literal["nasdaq", "sp500", "dowjones"] = Field(
        default="dowjones",
        description="The index for which we want to fetch the constituents.",
    )


class MajorIndicesConstituentsData(Data, BaseSymbol):
    """Major Indices Constituents Data."""

    name: str = Field(description="The name of the constituent company in the index.")
    sector: str = Field(
        description="The sector the constituent company in the index belongs to."
    )
    sub_sector: Optional[str] = Field(
        description="The sub-sector the constituent company in the index belongs to."
    )
    headquarter: Optional[str] = Field(
        description="The location of the headquarter of the constituent company in the index."
    )
    date_first_added: Optional[Union[date, str]] = Field(
        description="The date the constituent company was added to the index."
    )
    cik: int = Field(
        description="The Central Index Key of the constituent company in the index."
    )
    founded: Union[date, str] = Field(
        description="The founding year of the constituent company in the index."
    )
