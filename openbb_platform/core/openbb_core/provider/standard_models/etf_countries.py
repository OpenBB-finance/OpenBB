"""ETF Countries Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EtfCountriesQueryParams(QueryParams):
    """ETF Countries Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EtfCountriesData(Data):
    """ETF Countries Data."""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    country: str = Field(
        description="The country of the exposure.  Corresponding values are normalized percentage points."
    )
    weight: float = Field(
        description="The net exposure of the ETF to the country as a percentage of the total ETF assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
