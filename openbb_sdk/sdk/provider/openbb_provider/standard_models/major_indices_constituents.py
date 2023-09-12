"""Major Indices Constituents data model."""


from datetime import date
from typing import Literal, Union

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol


class MajorIndicesConstituentsQueryParams(QueryParams):
    """Major Indices Constituents Query."""

    index: Literal["nasdaq", "sp500", "dowjones"] = Field(
        default="dowjones",
        description="Index for which we want to fetch the constituents.",
    )


class MajorIndicesConstituentsData(Data, BaseSymbol):
    """Major Indices Constituents Data."""

    name: str = Field(description="Name of the constituent company in the index.")
    sector: str = Field(
        description="Sector the constituent company in the index belongs to."
    )
    sub_sector: str = Field(
        default=None,
        description="Sub-sector the constituent company in the index belongs to.",
    )
    headquarter: str = Field(
        default=None,
        description="Location of the headquarter of the constituent company in the index.",
    )
    date_first_added: Union[date, str] = Field(
        default=None, description="Date the constituent company was added to the index."
    )
    cik: int = Field(
        description="Central Index Key of the constituent company in the index."
    )
    founded: Union[date, str] = Field(
        description="Founding year of the constituent company in the index."
    )
