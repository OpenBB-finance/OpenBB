"""Index Sectors Standard Model."""

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class IndexSectorsQueryParams(QueryParams):
    """Index Sectors Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class IndexSectorsData(Data):
    """Index Sectors Data."""

    sector: str = Field(description="The sector name.")
    weight: float = Field(description="The weight of the sector in the index.")
