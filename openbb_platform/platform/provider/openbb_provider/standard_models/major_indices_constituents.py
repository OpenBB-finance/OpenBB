"""Major Indices Constituents data model."""

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class MajorIndicesConstituentsQueryParams(QueryParams):
    """Major Indices Constituents Query."""


class MajorIndicesConstituentsData(Data):
    """Major Indices Constituents Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="Name of the constituent company in the index.")
