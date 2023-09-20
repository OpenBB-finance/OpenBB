"""ETF Countries data model."""

from typing import List, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class EtfCountriesQueryParams(QueryParams):
    """ETF Countries Query Params"""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfCountriesData(Data):
    """ETF Countries Data."""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")

