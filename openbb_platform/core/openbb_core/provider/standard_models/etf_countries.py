"""ETF Countries Standard Model."""

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class EtfCountriesQueryParams(QueryParams):
    """ETF Countries Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (ETF)")

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EtfCountriesData(Data):
    """ETF Countries Data."""

    country: str = Field(
        description="The country of the exposure.  Corresponding values are normalized percentage points."
    )
