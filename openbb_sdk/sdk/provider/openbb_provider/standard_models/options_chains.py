"""Options Chains data model."""

from datetime import datetime
from typing import List, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class OptionsChainsQueryParams(QueryParams):
    """Options Chains Query Params"""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class OptionsChainsData(Data):
    """Options Chains Data."""

    expiration: datetime = Field(description="Expiration date of the contract.")
    strike: float = Field(description="Strike price of the contract.")
    option_type: str = Field(description="Call or Put.")
    contract_symbol: str = Field(description="Contract symbol for the option.")
    bid: float = Field(description="Bid price of the contract.")
    ask: float = Field(description="Ask price of the contract.")
    open_interest: float = Field(description="Open interest on the contract.")
    volume: float = Field(description="Current trading volume on the contract.")
