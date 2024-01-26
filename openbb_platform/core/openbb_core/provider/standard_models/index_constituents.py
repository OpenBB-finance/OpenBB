"""Index Constituents Standard Model."""

from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class IndexConstituentsQueryParams(QueryParams):
    """Index Constituents Query."""

    index: str = Field(
        description="Index to fetch the constituents of.",
    )


class IndexConstituentsData(Data):
    """Index Constituents Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(
        default=None, description="Name of the constituent company in the index."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
