"""ETF Sectors Standard Model."""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EtfSectorsQueryParams(QueryParams):
    """ETF Sectors Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (ETF)")

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EtfSectorsData(Data):
    """ETF Sectors Data."""

    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    sector: str = Field(description="Sector of exposure.")
    weight: float = Field(
        description="Sector exposure for the ETF as a percent of total assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
