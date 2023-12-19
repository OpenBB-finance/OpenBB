"""ETF Countries Standard Model."""

from typing import List, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class EtfCountriesQueryParams(QueryParams):
    """ETF Countries Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (ETF)")

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfCountriesData(Data):
    """ETF Countries Data."""

    country: str = Field(
        description="The country of the exposure.  Corresponding values are normalized percentage points."
    )
