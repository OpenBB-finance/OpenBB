"""Price target consensus data model."""


from typing import List, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class PriceTargetConsensusQueryParams(QueryParams):
    """Price Target Consensus Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class PriceTargetConsensusData(Data):
    """Price target consensus Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    target_high: float = Field(description="High target of the price target consensus.")
    target_low: float = Field(description="Low target of the price target consensus.")
    target_consensus: float = Field(
        description="Consensus target of the price target consensus."
    )
    target_median: float = Field(
        description="Median target of the price target consensus."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
