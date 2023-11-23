"""Index Sectors Standard Model."""

from typing import List, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class IndexSectorsQueryParams(QueryParams):
    """Index Sectors Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class IndexSectorsData(Data):
    """Index Sectors Data."""

    sector: str = Field(description="The sector name.")
    weight: float = Field(description="The weight of the sector in the index.")
