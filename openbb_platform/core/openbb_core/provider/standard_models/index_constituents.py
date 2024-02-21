"""Index Constituents Standard Model."""

from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class IndexConstituentsQueryParams(QueryParams):
    """Index Constituents Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))


class IndexConstituentsData(Data):
    """Index Constituents Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(
        default=None, description="Name of the constituent company in the index."
    )
