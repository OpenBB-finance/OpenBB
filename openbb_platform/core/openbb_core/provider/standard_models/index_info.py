"""Index Info Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class IndexInfoQueryParams(QueryParams):
    """Index Info Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class IndexInfoData(Data):
    """Index Info Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: str = Field(description="The name of the index.")
    description: str | None = Field(
        description="The short description of the index.", default=None
    )
    methodology: str | None = Field(
        description="URL to the methodology document.", default=None
    )
    factsheet: str | None = Field(
        description="URL to the factsheet document.", default=None
    )
    num_constituents: int | None = Field(
        description="The number of constituents in the index.", default=None
    )
